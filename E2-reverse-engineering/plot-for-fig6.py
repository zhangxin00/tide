import os
import re
import glob
import argparse
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rc('font', family='Linux Libertine O')
plt.rc('font', size=24)


def get_mac_logical_cpu_count():
    try:
        out = subprocess.check_output(
            ["sysctl", "-n", "hw.logicalcpu"],
            text=True
        ).strip()
        return int(out)
    except Exception:
        count = os.cpu_count()
        if count is None:
            raise RuntimeError("Failed to detect CPU count")
        return count


def find_latest_results_dir():
    candidates = [p for p in glob.glob("results_*") if os.path.isdir(p)]
    if not candidates:
        raise FileNotFoundError("No results_* directory found in the current directory")

    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


def make_default_output_name(base_dir):
    base_name = os.path.basename(os.path.abspath(base_dir))
    return f"q3a_{base_name}.png"


def parse_final_results(file_path):
    """
    解析 final_results.txt，格式类似：

    0
    sent 2528237 packets in 10000 ms

    7
    sum count is 513974
    6
    sum count is 522199

    返回：
      sent_count: int
      core_to_count: dict[int, int]
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    sent_count = None
    core_to_count = {}

    sent_pattern = re.compile(r"sent\s+(\d+)\s+packets\s+in\s+\d+\s+ms", re.IGNORECASE)
    sum_pattern = re.compile(r"sum count is\s+(\d+)", re.IGNORECASE)

    for line in lines:
        m = sent_pattern.fullmatch(line)
        if m:
            sent_count = int(m.group(1))
            break

    if sent_count is None:
        raise ValueError(f"Could not find sender packet count in {file_path}")
    if sent_count == 0:
        raise ValueError(f"Sender packet count is 0 in {file_path}")

    current_core = None
    for line in lines:
        if re.fullmatch(r"\d+", line):
            current_core = int(line)
            continue

        m = sum_pattern.fullmatch(line)
        if m and current_core is not None:
            core_to_count[current_core] = int(m.group(1))
            current_core = None

    return sent_count, core_to_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        default=None,
        help="Root directory containing 0_x folders. If omitted, auto-select the latest results_* directory."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output figure filename. If omitted, auto-generate from input directory name."
    )
    parser.add_argument(
        "--vmax",
        type=float,
        default=40,
        help="Heatmap vmax"
    )
    args = parser.parse_args()

    if args.input_dir is None:
        base_dir = find_latest_results_dir()
        print(f"Auto-selected latest results directory: {base_dir}")
    else:
        base_dir = args.input_dir

    if not os.path.isdir(base_dir):
        raise FileNotFoundError(f"Input directory does not exist: {base_dir}")

    output_path = args.output if args.output is not None else make_default_output_name(base_dir)

    # 读取 macOS 逻辑核心数
    n = get_mac_logical_cpu_count()
    print(f"Detected logical CPU count: {n}")
    print(f"Reading results from: {os.path.abspath(base_dir)}")
    print(f"Output figure: {output_path}")

    # receiver core 按真实编号显示：n-1, n-2, ..., 1
    receiver_cores = list(range(n - 1, 0, -1))

    # 列对应 0_1, 0_2, ..., 0_(n-1)
    receiver_counts = list(range(1, n))

    raw_data = []
    send = []

    # 先预读每一列的 sent_count
    for x in receiver_counts:
        folder = os.path.join(base_dir, f"0_{x}")
        file_path = os.path.join(folder, "final_results.txt")
        if not os.path.isfile(file_path):
            send.append(np.nan)
            continue

        try:
            sent_count, core_to_count = parse_final_results(file_path)
            send.append(sent_count)
        except Exception as e:
            print(f"Failed to parse sender count in {file_path}: {e}")
            send.append(np.nan)

    # 再构造 raw_data
    for core in receiver_cores:
        row = []
        for x in receiver_counts:
            folder = os.path.join(base_dir, f"0_{x}")
            file_path = os.path.join(folder, "final_results.txt")

            if not os.path.isfile(file_path):
                row.append(np.nan)
                continue

            try:
                sent_count, core_to_count = parse_final_results(file_path)

                if core in core_to_count:
                    row.append(core_to_count[core])
                else:
                    row.append(np.nan)
            except Exception as e:
                print(f"Failed to parse {file_path}: {e}")
                row.append(np.nan)

        raw_data.append(row)

    print("send =", send)
    print("raw_data =")
    for row in raw_data:
        print(row)

    # 按参考代码的方式生成 data_for_plot 和 annotations
    data_for_plot = []
    annotations = []

    for i in range(len(raw_data)):
        row_vals = []
        row_anns = []
        for j in range(len(raw_data[i])):
            val = raw_data[i][j]
            s = send[j]

            try:
                if np.isnan(val) or np.isnan(s) or val == 0:
                    row_vals.append(np.nan)
                    row_anns.append("")
                else:
                    normalized = s / val
                    row_vals.append(normalized)
                    row_anns.append(f"{normalized:.2f}")
            except Exception:
                row_vals.append(np.nan)
                row_anns.append("")

        data_for_plot.append(row_vals)
        annotations.append(row_anns)

    # 构建 DataFrame
    columns = list(range(1, len(receiver_counts) + 1))
    index = receiver_cores

    df_plot = pd.DataFrame(data_for_plot, columns=columns, index=index)
    df_annot = pd.DataFrame(annotations, columns=columns, index=index)

    # 绘图
    plt.figure(figsize=(18, 10))
    ax = sns.heatmap(
        df_plot,
        annot=df_annot,
        fmt="",
        cmap="Blues",
        linewidths=.5,
        vmin=0,
        vmax=args.vmax,
        cbar=True
    )

    ax.set_xlabel("Number of Receivers")
    ax.set_ylabel("Receiver Core")

    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    main()
