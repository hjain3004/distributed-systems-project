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


class TandemQueueAnalytical:
    """
    Analytical model for two-stage tandem queue (Li et al. 2015)

    System:
        Stage 1: λ → M/M/n₁ (broker)
        Network: D_link delay, probability p of failure
        Stage 2: Λ₂ = λ/(1-p) → M/M/n₂ (receiver)

    Key insight: Stage 2 sees HIGHER arrival rate due to retransmissions!
    """

    def __init__(self, lambda_arrival: float,
                 n1: int, mu1: float,
                 n2: int, mu2: float,
                 network_delay: float,
                 failure_prob: float):
        """
        Args:
            lambda_arrival: Arrival rate at Stage 1 (λ)
            n1: Number of broker servers
            mu1: Broker service rate (per server)
            n2: Number of receiver servers
            mu2: Receiver service rate (per server)
            network_delay: One-way network delay (D_link)
            failure_prob: Transmission failure probability (p)
        """
        self.lambda_ = lambda_arrival
        self.n1 = n1
        self.mu1 = mu1
        self.n2 = n2
        self.mu2 = mu2
        self.D_link = network_delay
        self.p = failure_prob

        # Stage 1 utilization
        self.rho1 = lambda_arrival / (n1 * mu1)

        # Stage 2 EFFECTIVE arrival rate (includes retries!)
        self.Lambda2 = lambda_arrival / (1 - failure_prob)
        self.rho2 = self.Lambda2 / (n2 * mu2)

        # Validate stability
        if self.rho1 >= 1.0:
            raise ValueError(f"Stage 1 unstable: ρ₁ = {self.rho1:.3f} >= 1")
        if self.rho2 >= 1.0:
            raise ValueError(f"Stage 2 unstable: ρ₂ = {self.rho2:.3f} >= 1")

        # Create M/M/N models for each stage
        self.stage1_model = MMNAnalytical(self.lambda_, self.n1, self.mu1)
        self.stage2_model = MMNAnalytical(self.Lambda2, self.n2, self.mu2)

    def stage1_waiting_time(self) -> float:
        """Mean waiting time at broker (Stage 1)"""
        return self.stage1_model.mean_waiting_time()

    def stage1_service_time(self) -> float:
        """Mean service time at broker"""
        return 1.0 / self.mu1

    def stage1_response_time(self) -> float:
        """Mean response time at broker (wait + service)"""
        return self.stage1_waiting_time() + self.stage1_service_time()

    def expected_network_time(self) -> float:
        """
        Expected network time including retries

        E[Network Time] = (2 + p) · D_link

        Derivation:
        - Initial transmission: D_link (broker → receiver)
        - ACK/NACK: D_link (receiver → broker)
        - Expected retries: p transmissions need retry
        - Each retry adds D_link (send) + D_link (ack) = 2·D_link
        - But simplified: (2 + p)·D_link captures average behavior

        Examples:
        - p=0 (no failures): 2·D_link (send + ack only)
        - p=0.2: 2.2·D_link (20% higher due to retries)
        - p=0.5: 2.5·D_link (50% higher due to retries)
        """
        return (2 + self.p) * self.D_link

    def stage2_waiting_time(self) -> float:
        """
        Mean waiting time at receiver (Stage 2)

        CRITICAL: Uses Λ₂ = λ/(1-p) as arrival rate!

        This is HIGHER than λ because failed transmissions retry,
        effectively increasing the load on Stage 2.
        """
        return self.stage2_model.mean_waiting_time()

    def stage2_service_time(self) -> float:
        """Mean service time at receiver"""
        return 1.0 / self.mu2

    def stage2_response_time(self) -> float:
        """Mean response time at receiver (wait + service)"""
        return self.stage2_waiting_time() + self.stage2_service_time()

    def total_message_delivery_time(self) -> float:
        """
        Total end-to-end message delivery time

        T_total = W₁ + S₁ + (2+p)·D_link + W₂ + S₂

        where:
          W₁ = waiting time at broker
          S₁ = service time at broker = 1/μ₁
          (2+p)·D_link = expected network time (send + ack + retries)
          W₂ = waiting time at receiver
          S₂ = service time at receiver = 1/μ₂

        This is Equation (X) from Li et al. (2015)
        """
        W1 = self.stage1_waiting_time()
        S1 = self.stage1_service_time()

        Network = self.expected_network_time()

        W2 = self.stage2_waiting_time()
        S2 = self.stage2_service_time()

        T_total = W1 + S1 + Network + W2 + S2
        return T_total

    def all_metrics(self) -> Dict[str, float]:
        """Return all analytical metrics"""
        return {
            # System parameters
            'lambda': self.lambda_,
            'Lambda2': self.Lambda2,
            'Lambda2_increase': (self.Lambda2 / self.lambda_ - 1) * 100,  # % increase
            'rho1': self.rho1,
            'rho2': self.rho2,

            # Stage 1 metrics
            'stage1_mean_wait': self.stage1_waiting_time(),
            'stage1_mean_service': self.stage1_service_time(),
            'stage1_mean_response': self.stage1_response_time(),
            'stage1_mean_queue_length': self.stage1_model.mean_queue_length(),

            # Network metrics
            'expected_network_time': self.expected_network_time(),
            'network_delay_factor': 2 + self.p,

            # Stage 2 metrics
            'stage2_mean_wait': self.stage2_waiting_time(),
            'stage2_mean_service': self.stage2_service_time(),
            'stage2_mean_response': self.stage2_response_time(),
            'stage2_mean_queue_length': self.stage2_model.mean_queue_length(),

            # End-to-end metrics
            'total_delivery_time': self.total_message_delivery_time(),
        }

    def compare_stages(self) -> None:
        """
        Print comparison showing Stage 2 has higher load

        Demonstrates the key insight: transmission failures increase
        Stage 2 arrival rate!
        """
        print(f"\n{'='*70}")
        print(f"Tandem Queue Analysis: Stage Comparison")
        print(f"{'='*70}")

        print(f"\nArrival Rates:")
        print(f"  Stage 1: λ₁ = {self.lambda_:.2f} msg/sec")
        print(f"  Stage 2: Λ₂ = λ/(1-p) = {self.Lambda2:.2f} msg/sec")
        print(f"  Increase: {((self.Lambda2/self.lambda_ - 1)*100):.1f}% higher at Stage 2!")

        print(f"\nUtilization:")
        print(f"  Stage 1: ρ₁ = {self.rho1:.3f}")
        print(f"  Stage 2: ρ₂ = {self.rho2:.3f}")
        if self.rho2 > self.rho1:
            print(f"  ⚠️  Stage 2 is MORE loaded than Stage 1 (bottleneck!)")

        print(f"\nWaiting Times:")
        print(f"  Stage 1: W₁ = {self.stage1_waiting_time():.6f} sec")
        print(f"  Stage 2: W₂ = {self.stage2_waiting_time():.6f} sec")

        print(f"\nTotal End-to-End Latency:")
        print(f"  T_total = {self.total_message_delivery_time():.6f} sec")
        print(f"  Breakdown:")
        print(f"    Stage 1: {self.stage1_response_time():.6f} sec ({self.stage1_response_time()/self.total_message_delivery_time()*100:.1f}%)")
        print(f"    Network: {self.expected_network_time():.6f} sec ({self.expected_network_time()/self.total_message_delivery_time()*100:.1f}%)")
        print(f"    Stage 2: {self.stage2_response_time():.6f} sec ({self.stage2_response_time()/self.total_message_delivery_time()*100:.1f}%)")
        print(f"{'='*70}\n")
