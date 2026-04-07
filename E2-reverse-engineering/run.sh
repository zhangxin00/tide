#!/bin/bash

# USAGE:
#   ./traffic2.sh
#   ./traffic2.sh 5
#
# If no parameter is passed, the script runs tests from the full candidate
# receiver count down to 1.
# If a parameter is passed, only that receiver count is tested.

SENDER_CORE=0

# Build candidate receiver cores: 7 down to 0, skipping SENDER_CORE.
candidate_cores=()
for core in {7..0}; do
    if [ "$core" -ne "$SENDER_CORE" ]; then
        candidate_cores+=("$core")
    fi
done

candidate_count=${#candidate_cores[@]}

if [ -n "$1" ]; then
    if ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 1 ] || [ "$1" -gt "$candidate_count" ]; then
        echo "Error: receiver count must be between 1 and $candidate_count"
        exit 1
    fi
    start=$1
    end=$1
else
    start=1
    end=$candidate_count
fi

for (( RECEIVER_NUMBERS=end; RECEIVER_NUMBERS>=start; RECEIVER_NUMBERS-- )); do
    echo "=============================================="
    echo "Starting test with RECEIVER_NUMBERS = $RECEIVER_NUMBERS"
    echo "=============================================="

    receiver_cores=("${candidate_cores[@]:0:$RECEIVER_NUMBERS}")
    receiver_count=${#receiver_cores[@]}

    rm -f sender.txt final_results.txt
    rm -rf rec output
    rm -f receiver_*.log sender.log

    # Launch receivers
    receiver_pids=()
    for core in "${receiver_cores[@]}"; do
        echo "Launching receiver on core $core"
        ./receiver "$core" > "receiver_${core}.log" 2>&1 &
        receiver_pids+=($!)
    done

    # Optional: give receivers a brief head start
    sleep 1

    # Launch sender
    echo "Launching sender on core $SENDER_CORE"
    ./sender "$SENDER_CORE" "$receiver_count" > sender.log 2>&1 &
    sender_pid=$!

    # Wait for sender to finish
    wait "$sender_pid" 2>/dev/null

    # Wait for all receivers to finish
    for pid in "${receiver_pids[@]}"; do
        wait "$pid" 2>/dev/null
    done

    mkdir -p output
    [ -f sender.log ] && mv sender.log output/
    for core in "${receiver_cores[@]}"; do
        [ -f "receiver_${core}.log" ] && mv "receiver_${core}.log" "output/receiver_${core}.log"
    done

    final_file="final_results.txt"
    {
        echo "$SENDER_CORE"

        if [ -f output/sender.log ]; then
            cat output/sender.log
        fi
        echo ""

        total=0
        for core in "${receiver_cores[@]}"; do
            if [ -f "output/receiver_${core}.log" ]; then
                val=$(awk '/sum count is/ {print $NF}' "output/receiver_${core}.log" | tail -n1)
                if [[ "$val" =~ ^[0-9]+$ ]]; then
                    total=$((total + val))
                fi
            fi
        done
        echo "$total"
        echo ""

        for core in "${receiver_cores[@]}"; do
            echo "$core"
            if [ -f "output/receiver_${core}.log" ]; then
                cat "output/receiver_${core}.log"
            fi
        done
    } > "$final_file"

    dest="${SENDER_CORE}_${receiver_count}"
    mkdir -p "$dest"

    [ -f final_results.txt ] && mv final_results.txt "$dest/"
    [ -d output ] && mv output "$dest/"
    [ -d rec ] && mv rec "$dest/" 2>/dev/null
    [ -f sender.txt ] && mv sender.txt "$dest/" 2>/dev/null

    echo "Test with RECEIVER_NUMBERS = $receiver_count completed. Results stored in directory: $dest"
    echo ""
done

ts=$(date +%Y%m%d_%H%M%S)
mkdir "results_$ts" && mv 0_[0-9]* "results_$ts/"

echo "All test loops completed."
