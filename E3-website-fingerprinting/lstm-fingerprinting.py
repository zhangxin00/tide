# Parts of this notebook are based on Prime+Probe 1, JavaScript 0
# Check out their repository: https://github.com/Yossioren/pp0


import os
import pickle
import random

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from keras.callbacks import EarlyStopping
from keras.layers import Conv1D, Dense, Dropout, Flatten, Input, LSTM, MaxPool1D
from keras.models import Model
from scipy.stats import ttest_ind_from_stats
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report,top_k_accuracy_score,  confusion_matrix, accuracy_score, ConfusionMatrixDisplay
from tensorflow.keras.optimizers import Adam
from tqdm.notebook import tqdm
from datetime import datetime,timedelta  # 用于计算时间
from sklearn import preprocessing
seed=7
UNITS=32
# fix random seed for reproducibility
np.random.seed(seed)
# ##### fix random seeds for reproducibility ########
SEED = 7
np.random.seed(SEED)
# def seed_tensorflow(seed=42):
#     os.environ['PYTHONHASHSEED'] = str(seed)
#     random.seed(seed)
#     np.random.seed(seed)
#     tf.random.set_seed(seed)
#     os.environ['TF_DETERMINISTIC_OPS'] = '1'
# seed_tensorflow(42)
import os
#os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "2"
LEN=5000

# 定义一些常用函数
# 保存日志
# fname是要保存的位置，s是要保存的内容
def log(fname, s):
    f = open(fname, 'a')
    f.write(str(datetime.now()) + ': ' + s + '\n')
    f.close()


def get_data(path, refresh=True, tor=False):
    # Data preparation
    traces = []
    labels = []

    if os.path.isdir(path):
        # If directory, find all .pkl files
        filepaths = [os.path.join(path, x) for x in os.listdir(path) if x.endswith(".pkl")]

        if not refresh and os.path.exists(os.path.join(path, "data.npz")):
            f = np.load(os.path.join(path, "data.npz"))
            return f["x"], f["y"], f["domains"]
    elif os.path.isfile(path):
        # If single file, just use this one
        filepaths = [path]
    else:
        raise RuntimeError

    for file in tqdm(filepaths):
        f = open(file, "rb")
        i=0
        while True:
            try:
                data = pickle.load(f)
                traces_i, labels_i = data[0][:LEN], data[1]
                i=i+1
               # if(i>20):
                 #   break



                if isinstance(traces_i[0], list):
                    traces.extend(traces_i)
                else:
                    traces.append(traces_i)

                labels.append(labels_i)
            except EOFError:
                print(file,i)
                break

    # Normalize traces
    traces = np.array(traces)

    if tor:
        traces = traces[:, 0:50000:100]
    else:
        traces = traces / traces.max(axis=1)[:, None]

    # Convert labels from domain names to ints
    domains = list(set(labels))
    int_mapping = {x: i for i, x in enumerate(domains)}
    labels = [int_mapping[x] for x in labels]
    labels = np.array(labels)

    if os.path.isdir(path):
        np.savez(os.path.join(path, "data.npz"), x=traces, y=labels, domains=domains)

    return traces, labels, domains


def cnn_lstm(input_vector, output_size=100, filters=256, strides=3, pool_size=4, units=UNITS, dropout=0.7, lr=0.001):
    inp = Input((input_vector, 1))
    x = Conv1D(filters, kernel_size=16, strides=strides, activation='relu')(inp)
    x = MaxPool1D(pool_size=pool_size, padding='same')(x)
    x = Conv1D(filters, kernel_size=8, strides=strides, activation='relu', padding='same')(x)
    x = MaxPool1D(pool_size=pool_size, padding='same')(x)
    x = LSTM(units, return_sequences=True, recurrent_activation='sigmoid')(x)
    x = Flatten()(x)
    x = Dropout(dropout)(x)
    preds = Dense(output_size, activation='softmax')(x)
    model = Model(inputs=inp, outputs=preds)
    opt = Adam(lr)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def small_cnn_lstm(input_vector, output_size=100, filters=256, strides=3, pool_size=4, units=32, dropout=0.7,
                   kernel_size=32, lr=0.001):
    inp = Input((input_vector, 1))
    x = Conv1D(filters, kernel_size=kernel_size, strides=strides, activation='relu')(inp)
    x = MaxPool1D(pool_size=pool_size, padding='same')(x)
    x = LSTM(units, return_sequences=True, recurrent_activation='sigmoid')(x)
    x = Flatten()(x)
    x = Dropout(dropout)(x)
    preds = Dense(output_size, activation='softmax')(x)
    model = Model(inputs=inp, outputs=preds)
    opt = Adam(lr)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def classify(X, y, n_validation=1, tor=True):
    X = X.reshape(*X.shape, -1)

    lab_enc = LabelEncoder()
    lab_hot = OneHotEncoder()
    y_num = lab_enc.fit_transform(y)
    y_hot = lab_hot.fit_transform(y_num.reshape(-1, 1))
    y_hot = y_hot.toarray()

    skf = StratifiedShuffleSplit(n_splits=10, random_state=666)

    preds = []
    true = []

    for train_index, test_index in tqdm(list(skf.split(X, y_num))[:n_validation]):
        X_train, X_test = X[train_index], X[test_index]
        mean = X_train.mean()
        std = X_train.std()
        X_train_norm = (X_train - mean + 1e-10) / std
        X_test_norm = (X_test - mean + 1e-10) / std

        y_train, y_test = y_hot[train_index], y_num[test_index]
        length = X_train.shape[1]

        if length < 2000:
            model = small_cnn_lstm(X_train.shape[1], output_size=np.unique(y).size)
        else:
            model = cnn_lstm(X_train.shape[1], output_size=np.unique(y).size)

        model.fit(
            X_train_norm,
            y_train,
            validation_split=0.1,
            epochs=10,
            verbose=2 if n_validation == 1 else 0,
            callbacks=[
                EarlyStopping(patience=2, restore_best_weights=True)
            ])

        print("top1 acc", np.mean([top_k_accuracy_score(true[i], preds[i], k=1) * 100 for i in range(len(true))]))
        print("top1 std", np.std([top_k_accuracy_score(true[i], preds[i], k=1) * 100 for i in range(len(true))]))

        print()
        preds.append(np.array(model.predict(X_test_norm)))
        true.append(np.array(y_test))

    return true, preds


def evaluate(path, open_world_path=None, n_validation=1, trace_length=LEN, tor=False, refresh=True,
             file_prefix="./", return_data=False, firstn_domains=-1):
    print(f"{file_prefix}{path}")


    X, y, domains = get_data(f"{file_prefix}{path}", tor=False, refresh=refresh)
    min_max_scaler = preprocessing.MinMaxScaler()

    #X = min_max_scaler.fit_transform(X)

    print(X[0])

    if firstn_domains != -1:
        found_y = set()
        i = 0

        while i < len(y):
            found_y.add(y[i])

            if len(found_y) > firstn_domains:
                break

            i += 1

        X = X[:i]
        y = y[:i]
        domains = domains[:i]

    if open_world_path is not None:
        X_ow, y_ow, _ = get_data(f"{file_prefix}{open_world_path}", tor=tor, refresh=refresh)
        y_ow[:, ] = y.max() + 1

        X = np.concatenate((X, X_ow))
        y = np.concatenate((y, y_ow))

    X = X[:, :trace_length]
    print(X.shape)
    true, preds = classify(X, y, n_validation=n_validation, tor=tor)
 #   result = confusion_matrix(true, preds, labels=range(100))
 #   disp = ConfusionMatrixDisplay(confusion_matrix=result)
 #   fig,ax=plt.subplots(figsize=(12,12))
 #   disp.plot(
 #   ax=ax,
#    include_values=True,  # 混淆矩阵每个单元格上显示具体数值
#    cmap="Greys",  # 配色
#    xticks_rotation="vertical",  # 同上

#    values_format="d"  # 显示的数值格式
#)
 #   ax.set_xlabel('Prediction')  # 横坐标轴标签
  #  ax.set_ylabel('True Label')  # 纵坐标轴标签
   # plt.tight_layout()
   # plt.savefig(testfile + '.jpg')
   # plt.show()
    print("top1 acc", np.mean([top_k_accuracy_score(true[i], preds[i], k=1) * 100 for i in range(len(true))]))
    print("top1 std", np.std([top_k_accuracy_score(true[i], preds[i], k=1) * 100 for i in range(len(true))]))
    print()
    print("top5 acc", np.mean([top_k_accuracy_score(true[i], preds[i], k=5) * 100 for i in range(len(true))]))
    print("top5 std", np.std([top_k_accuracy_score(true[i], preds[i], k=5) * 100 for i in range(len(true))]))
    log_string = ('testfile: {:s} seed={:s} trace_len={:s}\n'
                  'top1 acc/std: [{:0.6f}/{:0.6f}],top5 acc/std: [{:0.6f}/{:0.6f}] ').format(
         path, str(seed), str(LEN),
        np.mean([top_k_accuracy_score(true[i], preds[i], k=1) * 100 for i in range(len(true))]),
        np.std([top_k_accuracy_score(true[i], preds[i], k=1) * 100 for i in range(len(true))]),
        np.mean([top_k_accuracy_score(true[i], preds[i], k=5) * 100 for i in range(len(true))]),
        np.std([top_k_accuracy_score(true[i], preds[i], k=5) * 100 for i in range(len(true))])
    )
    # 服务器一般用的世界时，需要加8个小时，可以视情况把加8小时去掉
    print(str(datetime.now() + timedelta(hours=8)) + ': ')
    print(log_string)  # 打印日志
    log('./Fingerprinting.log', log_string)  # 保存日志

    if return_data:
        return true, preds, domains
#21.4 for tor default

#testfile='laptop/tick-default-taskset'
testfile='safari-full'
#testfile='tide-m3pro'
true, preds, domains = evaluate(testfile, n_validation=10, return_data=True,refresh=True,tor=False)

