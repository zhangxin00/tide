# Fingerprinting Websites with TIDE

## Setup and Execution

1. Compile the code and install the required Python packages on the Apple test machine:

   ```bash
   make
   pip3 install -r requirements.txt
   ```

2. Enable the required Safari and macOS permissions:

   - In **Safari**, enable remote automation:

     **Safari -> Settings -> Show features for web developers**

     Then open:

     **Develop -> Developer Settings -> Developer -> Automation -> Allow remote automation**

   - In **System Settings**, allow Terminal to control your computer:

     **System Settings -> Privacy & Security -> Accessibility**

3. Run the small-scale experiment on 5 websites:

   a. Record the side-channel traces:

   ```bash
   python3 record_data.py --num_runs 40 --browser safari --trace_length 5 --sites_list alexa5 --out_directory safari-experiment
   ```

   b. Evaluate the attack results:

   ```bash
   python3 scripts/check_results.py --data_file safari-experiment
   ```

4. Optionally, run the full experiment on 100 websites:

   a. Record the side-channel traces:

   ```bash
   python3 record_data.py --num_runs 100 --browser safari --trace_length 5 --sites_list alexa100 --out_directory safari-full
   ```

   b. Install TensorFlow 2.x on the GPU server and run the classifier on the collected `safari-full` dataset:

   ```bash
   pip3 install tensorflow==2.6.0
   python3 lstm-fingerprinting.py
   ```

## Expected Results

For Step 3, the top-1 accuracy should be higher than random guessing, which is 20% in this example with 5 websites.

Example output:

```text
python3 scripts/check_results.py --data_file safari-experiment

Analyzing results from safari-experiment
100%|███████████████████████████████████████████| 10/10 [00:01<00:00, 5.61it/s]

Number of traces: 200

top1 accuracy: 81.3% (+/- 5.1%)
top5 accuracy: 100.0% (+/- 0.0%)
```

For Step 4, the top-1 accuracy should be much higher than random guessing, which is 1% in this example with 100 websites.

Example output:

```text
top1 acc/std: [93.810000/0.690217],top5 acc/std: [98.720000/0.193907]
```
