"""
Verify Pareto distribution mathematical formulas

Check if CV² = 1/(α-2) or CV² = 1/(α(α-2))
"""

import numpy as np

def pareto_theoretical_cv_squared(alpha):
    """Calculate CV² from first principles

    For Pareto Type I with PDF f(t) = α·k^α / t^(α+1):
    - E[T] = α·k/(α-1)
    - E[T²] = α·k²/(α-2) for α > 2
    - Var[T] = E[T²] - (E[T])²
    - CV² = Var[T] / (E[T])²
    """
    if alpha <= 2:
        return float('inf')

    # Using k=1 for simplicity (doesn't affect CV²)
    k = 1.0

    # Mean
    mean = alpha * k / (alpha - 1)

    # Second moment
    second_moment = alpha * k**2 / (alpha - 2)

    # Variance
    variance = second_moment - mean**2

    # CV²
    cv_squared = variance / mean**2

    print(f"\nα = {alpha}:")
    print(f"  E[T] = {mean:.6f}")
    print(f"  E[T²] = {second_moment:.6f}")
    print(f"  Var[T] = {variance:.6f}")
    print(f"  CV² = {cv_squared:.6f}")
    print(f"  Formula 1/(α-2) = {1/(alpha-2):.6f}")
    print(f"  Formula 1/(α(α-2)) = {1/(alpha*(alpha-2)):.6f}")

    return cv_squared


print("="*70)
print("Deriving CV² for Pareto Distribution")
print("="*70)

for alpha in [2.1, 2.5, 3.0]:
    cv2 = pareto_theoretical_cv_squared(alpha)

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("From first principles: CV² = 1/(α(α-2)), NOT 1/(α-2)")
print("="*70)
