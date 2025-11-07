"""Analytical queueing formulas (Equations 1-15)"""

import numpy as np
from scipy import special
from typing import Dict, Any


class MMNAnalytical:
    """M/M/N analytical formulas (Equations 1-5)"""

    def __init__(self, arrival_rate: float, num_threads: int, service_rate: float):
        """
        Args:
            arrival_rate: λ (messages/sec)
            num_threads: N (number of threads)
            service_rate: μ (messages/sec per thread)
        """
        self.lambda_ = arrival_rate
        self.N = num_threads
        self.mu = service_rate

        # Derived quantities
        self.rho = self.utilization()
        self.a = self.traffic_intensity()

        if self.rho >= 1.0:
            raise ValueError(f"System unstable: ρ = {self.rho:.3f} >= 1")

    def utilization(self) -> float:
        """Equation 1: ρ = λ/(N·μ)"""
        return self.lambda_ / (self.N * self.mu)

    def traffic_intensity(self) -> float:
        """Traffic intensity: a = λ/μ"""
        return self.lambda_ / self.mu

    def prob_zero(self) -> float:
        """
        Equation 2: P₀ (Erlang-C formula)

        P₀ = [Σ(n=0 to N-1) aⁿ/n! + aᴺ/(N!(1-ρ))]⁻¹
        """
        # Sum term: Σ(n=0 to N-1) aⁿ/n!
        sum_term = sum(
            (self.a ** n) / special.factorial(n)
            for n in range(self.N)
        )

        # Last term: aᴺ/(N!(1-ρ))
        last_term = (self.a ** self.N) / (special.factorial(self.N) * (1 - self.rho))

        P0 = 1.0 / (sum_term + last_term)
        return P0

    def erlang_c(self) -> float:
        """
        Equation 3: C(N, a) - Probability of queueing (Erlang-C)

        C(N,a) = [aᴺ/(N!(1-ρ))] · P₀
        """
        P0 = self.prob_zero()
        numerator = (self.a ** self.N)
        denominator = special.factorial(self.N) * (1 - self.rho)

        C = (numerator / denominator) * P0
        return C

    def mean_queue_length(self) -> float:
        """
        Equation 4: Lq - Mean number of messages waiting

        Lq = C(N,a) · ρ/(1-ρ)
        """
        C = self.erlang_c()
        Lq = C * self.rho / (1 - self.rho)
        return Lq

    def mean_waiting_time(self) -> float:
        """
        Equation 5: Wq - Mean waiting time (Little's Law)

        Wq = Lq / λ
        """
        Lq = self.mean_queue_length()
        Wq = Lq / self.lambda_
        return Wq

    def mean_response_time(self) -> float:
        """
        Mean response time: R = Wq + 1/μ
        """
        Wq = self.mean_waiting_time()
        return Wq + (1.0 / self.mu)

    def mean_system_size(self) -> float:
        """
        Mean number in system: L = Lq + λ/μ
        """
        Lq = self.mean_queue_length()
        return Lq + self.a

    def all_metrics(self) -> Dict[str, float]:
        """Return all analytical metrics"""
        return {
            'utilization': self.utilization(),
            'traffic_intensity': self.traffic_intensity(),
            'prob_zero': self.prob_zero(),
            'erlang_c': self.erlang_c(),
            'mean_queue_length': self.mean_queue_length(),
            'mean_waiting_time': self.mean_waiting_time(),
            'mean_response_time': self.mean_response_time(),
            'mean_system_size': self.mean_system_size(),
        }


class MGNAnalytical:
    """M/G/N analytical formulas (Equations 6-10)"""

    def __init__(self, arrival_rate: float, num_threads: int,
                 mean_service: float, variance_service: float):
        """
        Args:
            arrival_rate: λ
            num_threads: N
            mean_service: E[S]
            variance_service: Var[S]
        """
        self.lambda_ = arrival_rate
        self.N = num_threads
        self.ES = mean_service
        self.VarS = variance_service

        # Service rate
        self.mu = 1.0 / mean_service

        # Utilization
        self.rho = arrival_rate / (num_threads * self.mu)

        if self.rho >= 1.0:
            raise ValueError(f"System unstable: ρ = {self.rho:.3f} >= 1")

    def coefficient_of_variation(self) -> float:
        """
        Equation 9: C² = Var[S] / E[S]²
        """
        if self.ES == 0:
            return 0.0
        return self.VarS / (self.ES ** 2)

    def mean_waiting_time_mg1(self) -> float:
        """
        Equation 10: Wq for M/G/1 (Pollaczek-Khinchine)

        Wq = (ρ/(1-ρ)) · (E[S²]/(2·E[S]))
           = (ρ/(1-ρ)) · (E[S]/2) · (1 + C²)
        """
        C_squared = self.coefficient_of_variation()

        Wq = (self.rho / (1 - self.rho)) * (self.ES / 2) * (1 + C_squared)
        return Wq

    def mean_waiting_time_mgn(self) -> float:
        """
        Equation 10 (extended): Wq for M/G/N (approximation)

        Standard approximation from queueing theory:
        Wq(M/G/N) ≈ Wq(M/M/N) × (1 + C²) / 2

        This adjusts the M/M/N baseline by the service time variability.
        When C²=1 (exponential), this gives Wq(M/M/N).
        """
        # Get baseline M/M/N waiting time
        mmn = MMNAnalytical(self.lambda_, self.N, self.mu)
        Wq_mmn = mmn.mean_waiting_time()

        C_squared = self.coefficient_of_variation()

        # Apply variability correction factor
        Wq = Wq_mmn * (1 + C_squared) / 2
        return Wq

    def mean_response_time(self) -> float:
        """Mean response time: R = Wq + E[S]"""
        return self.mean_waiting_time_mgn() + self.ES

    def p99_response_time(self) -> float:
        """
        Equation 15: R99 ≈ E[R] + 2.33·σR

        Using approximation: σR ≈ √(Var[Wq] + Var[S])
        For M/G/N, Var[Wq] is approximated from heavy-tail impact
        """
        mean_R = self.mean_response_time()

        # Approximate variance (conservative estimate for heavy tails)
        C_squared = self.coefficient_of_variation()
        var_R_approx = self.VarS * (1 + C_squared)
        sigma_R = np.sqrt(var_R_approx)

        # 99th percentile (z = 2.33 for normal approximation)
        R99 = mean_R + 2.33 * sigma_R
        return R99

    def all_metrics(self) -> Dict[str, float]:
        """Return all analytical metrics"""
        return {
            'utilization': self.rho,
            'mean_service': self.ES,
            'var_service': self.VarS,
            'cv_squared': self.coefficient_of_variation(),
            'mean_waiting_time': self.mean_waiting_time_mgn(),
            'mean_response_time': self.mean_response_time(),
            'p99_response_time': self.p99_response_time(),
        }


class ThreadingAnalytical:
    """Threading model analytical formulas (Equations 11-15)"""

    @staticmethod
    def dedicated_max_connections(num_threads: int, threads_per_connection: int = 2) -> int:
        """
        Equation 11: Nmax_connections = Nthreads / 2
        """
        return num_threads // threads_per_connection

    @staticmethod
    def dedicated_throughput(arrival_rate: float, num_threads: int,
                            service_rate: float) -> float:
        """
        Equation 12: Xdedicated = min(λ, (Nthreads/2)·μ)
        """
        max_capacity = (num_threads / 2) * service_rate
        return min(arrival_rate, max_capacity)

    @staticmethod
    def shared_effective_service_rate(service_rate: float, num_active: int,
                                      num_threads: int, overhead: float = 0.1) -> float:
        """
        Equation 13: μeff = μ / (1 + α·Nactive/Nthreads)
        """
        if num_threads == 0:
            return 0.0
        overhead_factor = 1 + overhead * (num_active / num_threads)
        return service_rate / overhead_factor

    @staticmethod
    def thread_saturation_probability(mmn: MMNAnalytical) -> float:
        """
        Equation 14: Psaturate = P(Nbusy = N)

        Uses Erlang-C formula
        """
        return mmn.erlang_c() * mmn.rho
