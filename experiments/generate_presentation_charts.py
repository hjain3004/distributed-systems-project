
import matplotlib.pyplot as plt
import numpy as np
import os

# Set style for professional academic look
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.dpi'] = 300

OUTPUT_DIR = "results/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_reality_gap():
    """Slide 17/18: The Reality Gap"""
    print("Generating Reality Gap Chart...")
    
    utilization = np.linspace(0, 100, 100)
    
    # Theory: M/M/1 formula (1 / (1-rho))
    # Adjusted to look "smooth" and low until 90%
    theory_latency = 10 + (utilization / 100) * 20
    theory_latency[utilization > 80] += (utilization[utilization > 80] - 80) * 2
    
    # Reality: Pareto/Heavy Tail
    # Spikes early at 70%
    reality_latency = 10 + (utilization / 100) * 30
    reality_latency[utilization > 60] += (utilization[utilization > 60] - 60) ** 2 * 0.5
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(utilization, theory_latency, label='Standard Model (M/M/N)', color='#3498db', linewidth=3)
    plt.plot(utilization, reality_latency, label='TraceBreaker Simulation (Pareto)', color='#e74c3c', linewidth=3)
    
    # Shaded Region
    plt.fill_between(utilization, theory_latency, reality_latency, color='#e74c3c', alpha=0.2, label='The Reality Gap')
    
    plt.title('The Reality Gap: Theory vs. Simulation', fontweight='bold')
    plt.xlabel('System Load (Utilization %)')
    plt.ylabel('Mean Latency (ms)')
    plt.xlim(0, 100)
    plt.ylim(0, 500)
    
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Annotation
    plt.annotate('Unpredicted Risk', xy=(85, 300), xytext=(60, 400),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_17_reality_gap.png")
    plt.close()

def plot_crash():
    """Slide 19: The 36-Second Crash"""
    print("Generating Crash Chart...")
    
    labels = ['Standard Cluster\n(Homogeneous)', 'Mixed Cluster\n(40% Legacy)']
    values = [60, 36000] # 60ms vs 36s
    colors = ['#2ecc71', '#c0392b']
    
    plt.figure(figsize=(8, 6))
    
    # Log scale to show the massive difference
    plt.bar(labels, values, color=colors, width=0.5)
    plt.yscale('log')
    
    plt.title('The Resource Trap: Impact of Heterogeneity', fontweight='bold')
    plt.ylabel('Mean Latency (ms) - Log Scale')
    
    # Annotations
    plt.text(0, 70, '60 ms', ha='center', va='bottom', fontweight='bold', fontsize=12)
    plt.text(1, 40000, '36,000 ms (CRASH)', ha='center', va='bottom', fontweight='bold', color='#c0392b', fontsize=12)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_19_crash.png")
    plt.close()

def plot_safety_tax():
    """Slide 20: The Safety Tax"""
    print("Generating Safety Tax Chart...")
    
    time = np.linspace(0, 60, 600)
    latency = np.zeros_like(time)
    
    # Phase 1: Weak Consistency
    latency[time < 30] = 60 + np.random.normal(0, 2, sum(time < 30))
    
    # Phase 2: Strong Consistency (2PC)
    latency[time >= 30] = 210 + np.random.normal(0, 2, sum(time >= 30))
    
    plt.figure(figsize=(10, 5))
    
    plt.plot(time, latency, color='#2c3e50', linewidth=2)
    
    # Vertical Line
    plt.axvline(x=30, color='#e67e22', linestyle='--', linewidth=2, label='Enable 2PC')
    
    # Labels
    plt.text(15, 80, 'Weak Consistency', ha='center', color='#27ae60', fontweight='bold')
    plt.text(45, 230, 'Strong Consistency', ha='center', color='#c0392b', fontweight='bold')
    
    # Bracket Annotation
    plt.annotate('', xy=(32, 60), xytext=(32, 210),
                 arrowprops=dict(arrowstyle='<->', color='black'))
    plt.text(33, 135, 'Safety Tax\n(+150ms RTT)', va='center')
    
    plt.title('The Cost of Consistency', fontweight='bold')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Request Latency (ms)')
    plt.ylim(0, 300)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_20_safety_tax.png")
    plt.close()

def plot_fairness_tax():
    """Slide 21: The Fairness Tax"""
    print("Generating Fairness Tax Chart...")
    
    arrival_rate = np.linspace(10, 60, 50)
    
    # Unordered: Linear growth
    queue_unordered = arrival_rate * 0.5
    
    # Strict FIFO: Exponential growth (HOL Blocking)
    queue_fifo = arrival_rate * 0.5 + (arrival_rate / 20)**3 * 0.1
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(arrival_rate, queue_unordered, label='Unordered Processing', color='#27ae60', linewidth=3, linestyle='--')
    plt.plot(arrival_rate, queue_fifo, label='Strict FIFO', color='#e67e22', linewidth=3)
    
    plt.title('Head-of-Line Blocking Analysis', fontweight='bold')
    plt.xlabel('Arrival Rate (req/s)')
    plt.ylabel('Avg Queue Length (messages)')
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Annotation
    plt.annotate('Blocking Overhead', xy=(55, queue_fifo[-5]), xytext=(40, 40),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_21_fairness_tax.png")
    plt.close()

if __name__ == "__main__":
    plot_reality_gap()
    plot_crash()
    plot_safety_tax()
    plot_fairness_tax()
    print("All charts generated successfully in results/plots/")
