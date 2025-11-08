#!/bin/bash

echo "========================================="
echo "Testing Distributed Systems Features"
echo "========================================="

# Test 1: Cloud Message Broker
echo -e "\n[1/4] Testing Cloud Message Broker..."
python3 experiments/cloud_broker_simulation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "      ✓ Cloud broker tests PASSED"
else
    echo "      ✗ Cloud broker tests FAILED"
    exit 1
fi

# Test 2: Distributed Systems
echo -e "\n[2/4] Testing Distributed Systems (Raft + Vector Clocks + CAP)..."
python3 experiments/distributed_systems_validation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "      ✓ Distributed systems tests PASSED"
else
    echo "      ✗ Distributed systems tests FAILED"
    exit 1
fi

# Test 3: Two-Phase Commit
echo -e "\n[3/4] Testing Two-Phase Commit..."
python3 experiments/two_phase_commit_validation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "      ✓ 2PC tests PASSED"
else
    echo "      ✗ 2PC tests FAILED"
    exit 1
fi

# Test 4: CAP Analysis
echo -e "\n[4/4] Testing CAP Theorem Analysis..."
python3 -m src.analysis.cap_analysis > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "      ✓ CAP analysis PASSED"
else
    echo "      ✗ CAP analysis FAILED"
    exit 1
fi

echo -e "\n========================================="
echo "✓ All tests completed successfully!"
echo "========================================="

# Check for generated files
echo -e "\nGenerated files:"
ls -lh experiments/*.csv 2>/dev/null | awk '{print "  -", $9}'

echo -e "\nTo view detailed output, run individual experiments:"
echo "  python3 experiments/cloud_broker_simulation.py"
echo "  python3 experiments/distributed_systems_validation.py"
echo "  python3 experiments/two_phase_commit_validation.py"
