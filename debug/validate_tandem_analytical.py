"""
Quick validation: Tandem queue analytical formulas

Verifies that the two-stage model is implemented correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.analysis.analytical import TandemQueueAnalytical


def test_stage2_arrival_rate():
    """Test that Λ₂ = λ/(1-p) is calculated correctly"""
    
    print("="*70)
    print("TEST 1: Stage 2 Arrival Rate Formula")
    print("="*70)
    
    test_cases = [
        {'lambda': 100, 'p': 0.0, 'expected': 100.0, 'n2': 10},
        {'lambda': 100, 'p': 0.1, 'expected': 111.11, 'n2': 10},
        {'lambda': 100, 'p': 0.2, 'expected': 125.0, 'n2': 12},
        {'lambda': 100, 'p': 0.5, 'expected': 200.0, 'n2': 20},
    ]

    all_passed = True

    for test in test_cases:
        analytical = TandemQueueAnalytical(
            lambda_arrival=test['lambda'],
            n1=10, mu1=12,
            n2=test['n2'], mu2=12,
            network_delay=0.01,
            failure_prob=test['p']
        )
        
        calculated = analytical.Lambda2
        expected = test['expected']
        error = abs(calculated - expected) / expected * 100 if expected > 0 else 0
        
        passed = error < 0.1  # 0.1% tolerance
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"\n  λ={test['lambda']}, p={test['p']}")
        print(f"    Expected Λ₂: {expected:.2f}")
        print(f"    Calculated:  {calculated:.2f}")
        print(f"    Error: {error:.4f}%  {status}")
        
        if not passed:
            all_passed = False
    
    print(f"\n{'='*70}")
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print(f"{'='*70}\n")
    
    return all_passed


def test_stability_validation():
    """Test that configuration rejects unstable systems"""
    
    print("="*70)
    print("TEST 2: Stability Validation")
    print("="*70)
    
    # Should PASS (stable)
    print("\n  Test 2a: Stable system (should succeed)...")
    try:
        config = TandemQueueConfig(
            arrival_rate=100,
            n1=10, mu1=12,
            n2=12, mu2=12,  # Extra capacity for Stage 2
            network_delay=0.01,
            failure_prob=0.2,  # Λ₂ = 125
            sim_duration=100,
            warmup_time=10
        )
        print(f"    ρ₁ = {config.stage1_utilization:.3f}")
        print(f"    Λ₂ = {config.stage2_effective_arrival:.1f}")
        print(f"    ρ₂ = {config.stage2_utilization:.3f}")
        print("    ✓ PASS: Stable system accepted")
        test_2a_passed = True
    except ValueError as e:
        print(f"    ✗ FAIL: {e}")
        test_2a_passed = False
    
    # Should FAIL (unstable Stage 2)
    print("\n  Test 2b: Unstable Stage 2 (should reject)...")
    try:
        config = TandemQueueConfig(
            arrival_rate=100,
            n1=10, mu1=12,
            n2=10, mu2=12,  # Same capacity as Stage 1
            network_delay=0.01,
            failure_prob=0.2,  # Λ₂ = 125 > capacity!
            sim_duration=100,
            warmup_time=10
        )
        print("    ✗ FAIL: Unstable system was accepted!")
        test_2b_passed = False
    except ValueError as e:
        print(f"    ✓ PASS: Correctly rejected unstable system")
        print(f"    Reason: {e}")
        test_2b_passed = True
    
    print(f"\n{'='*70}")
    if test_2a_passed and test_2b_passed:
        print("✓ ALL STABILITY TESTS PASSED")
    else:
        print("✗ SOME STABILITY TESTS FAILED")
    print(f"{'='*70}\n")
    
    return test_2a_passed and test_2b_passed


def test_network_time_formula():
    """Test that network time formula (2+p)·D is correct"""
    
    print("="*70)
    print("TEST 3: Network Time Formula")
    print("="*70)
    
    test_cases = [
        {'D': 0.01, 'p': 0.0, 'expected': 0.020, 'n2': 10},  # 2·D
        {'D': 0.01, 'p': 0.1, 'expected': 0.021, 'n2': 10},  # 2.1·D
        {'D': 0.01, 'p': 0.3, 'expected': 0.023, 'n2': 15},  # 2.3·D (changed from 0.5)
    ]

    all_passed = True

    for test in test_cases:
        analytical = TandemQueueAnalytical(
            lambda_arrival=100,
            n1=10, mu1=12,
            n2=test['n2'], mu2=12,
            network_delay=test['D'],
            failure_prob=test['p']
        )
        
        calculated = analytical.expected_network_time()
        expected = test['expected']
        error = abs(calculated - expected) / expected * 100 if expected > 0 else 0
        
        passed = error < 0.1
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"\n  D={test['D']}, p={test['p']}")
        print(f"    Expected: (2+{test['p']})×{test['D']} = {expected:.6f}")
        print(f"    Calculated: {calculated:.6f}")
        print(f"    Error: {error:.4f}%  {status}")
        
        if not passed:
            all_passed = False
    
    print(f"\n{'='*70}")
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print(f"{'='*70}\n")
    
    return all_passed


def main():
    """Run all tandem queue validation tests"""
    
    print("\n" + "="*70)
    print(" TANDEM QUEUE ANALYTICAL VALIDATION")
    print("="*70)
    
    test1 = test_stage2_arrival_rate()
    test2 = test_stability_validation()
    test3 = test_network_time_formula()
    
    print("\n" + "="*70)
    print(" VALIDATION SUMMARY")
    print("="*70)
    print(f"  Stage 2 arrival rate: {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"  Stability validation: {'✓ PASS' if test2 else '✗ FAIL'}")
    print(f"  Network time formula: {'✓ PASS' if test3 else '✗ FAIL'}")
    
    if test1 and test2 and test3:
        print("\n✓ ALL VALIDATION TESTS PASSED")
        print("  Tandem queue analytical model is correct!")
    else:
        print("\n✗ SOME VALIDATION TESTS FAILED")
        print("  Review implementation!")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
