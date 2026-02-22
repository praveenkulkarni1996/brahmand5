## Integration Test Leak Check Script

To ensure the integration tests for the `greet` application are robust and properly clean up child processes, the following script can be used. It runs the integration tests multiple times and verifies that no `greet` server instances are left running after each test run.

### Usage:
1.  Save the script to a file (e.g., `run_leak_check.sh`).
2.  Make it executable: `chmod +x run_leak_check.sh`.
3.  Run it from the project root directory: `./run_leak_check.sh`.

### Script:
```bash
#!/bin/bash

# Ensure the greet application is built in debug mode
echo "Building greet application in debug mode..."
cargo build --package greet

# Set the number of iterations
NUM_ITERATIONS=30
LEAK_DETECTED=0

echo "Running integration tests $NUM_ITERATIONS times and checking for process leaks..."

for i in $(seq 1 $NUM_ITERATIONS); do
    echo "--- Iteration $i/$NUM_ITERATIONS ---"

    # Run tests
    if ! cargo test --workspace --test "integration_test" --package greet --color always --no-fail-fast; then
        echo "ERROR: 'cargo test' failed in iteration $i. Check test output above."
        LEAK_DETECTED=1
        break
    fi

    # Check for Leaked Processes
    if ps aux | grep -v grep | grep -q 'target/debug/greet'; then
        echo "ERROR: Leaked 'greet' process(es) detected after iteration $i!"
        ps aux | grep -v grep | grep 'target/debug/greet'
        LEAK_DETECTED=1
        break
    fi
done

if [ $LEAK_DETECTED -eq 0 ]; then
    echo "SUCCESS: All $NUM_ITERATIONS iterations completed with no 'greet' processes leaked."
else
    echo "FAILURE: One or more issues detected during the test run."
    exit 1
fi
```
