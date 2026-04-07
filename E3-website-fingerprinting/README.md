# Fingerprinting websites using TIDE

1.  Run `make` to compile our code, and  run `pip3 install -r requirements.txt` to install necessary packages on the test Apple machine.
2.  Allow remote automation in the Developer section in Safari setting (Safari -> Settings -> (check) Show features for web developers and Develop -> Developer Settings -> Developer -> Automation -> (check) Allow remote automation. 
    Allow the Terminal to control your computer in system setting (System Settings -> Privacy & Security settings -> Accessibility) 
3.a  Run `python3 record_data.py --num_runs 40 --browser safari --trace_length 5 --sites_list alexa5 --out_directory safari-experiment` to record the side channel traces.
3.b  Run `python3 scripts/check_results.py --data_file safari-experiment` to check attack results.
4.a (optional) Run `python3 record_data.py --num_runs 100 --browser safari --trace_length 5 --sites_list alexa100 --out_directory safari-full` to record the side channel traces. 
4.b (optional) Install Tensorflow 2.x on the GPU server using `pip3 install tensorflow==2.6.0`and then run the classifier on the collected safari-full dataset `python3 lstm-fingerprinting.py`.

# Expected results

When running step 3, the top-1 accuracy is higher than random guess (20% in our example that contains 5 websites).

```
python scripts/check_results.py --data_file safari-experiment

Analyzing results from readme-experiment
100%|███████████████████████████████████████████| 10/10 [00:01<00:00,  5.61it/s]

Number of traces: 200

top1 accuracy: 81.3% (+/- 5.1%)
top5 accuracy: 100.0% (+/- 0.0%)
```

For step 4, the top-1 accuracy is much higher than random guess (1% in our example that contains 100 websites).

```
...
top1 acc/std: [93.810000/0.690217],top5 acc/std: [98.420000/0.193907] 
```
