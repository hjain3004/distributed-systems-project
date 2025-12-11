
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

def plot_work_stealing():
    """Slide 22: The Work Stealing Fix"""
    print("Generating Work Stealing Chart...")
    
    labels = ['Naive Routing\n(No Stealing)', 'Work Stealing\nActive']
    values = [36000, 250] # 36s vs 250ms
    colors = ['#c0392b', '#27ae60']
    
    plt.figure(figsize=(8, 6))
    
    # Log scale to show the massive difference
    bars = plt.bar(labels, values, color=colors, width=0.5)
    plt.yscale('log')
    
    plt.title('Impact of Work Stealing on Heterogeneous Clusters', fontweight='bold')
    plt.ylabel('Mean Latency (ms) - Log Scale')
    
    # Annotations
    plt.text(0, 40000, '36,000 ms\n(Legacy Node Saturation)', ha='center', va='bottom', fontweight='bold', color='#c0392b', fontsize=11)
    plt.text(1, 300, '250 ms\n(Balanced Load)', ha='center', va='bottom', fontweight='bold', color='#27ae60', fontsize=11)
    
    # Add Checkmark to Green Bar
    plt.text(1, 150, '✓ Stable', ha='center', va='top', color='white', fontweight='bold')

    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_22_work_stealing.png")
    plt.close()

def plot_load_shedding():
    """Slide 23: The Load Shedding Safety Valve"""
    print("Generating Load Shedding Chart...")
    
    time = np.linspace(0, 10, 100)
    
    # Unbounded: Exponential growth
    latency_unbounded = 50 * np.exp(time * 0.8)
    
    # Capped: Rises then hits ceiling
    latency_capped = 50 * np.exp(time * 0.8)
    ceiling = 500 # Rejection Threshold
    latency_capped = np.minimum(latency_capped, ceiling)
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(time, latency_unbounded, label='Unbounded Queue (Crash)', color='#7f8c8d', linestyle='--', linewidth=2)
    plt.plot(time, latency_capped, label='TraceBreaker (Capped at K=50)', color='#2980b9', linewidth=3)
    
    # Horizontal Line
    plt.axhline(y=ceiling, color='#e74c3c', linestyle=':', linewidth=2)
    plt.text(0.5, ceiling + 100, 'Rejection Threshold', color='#e74c3c', fontweight='bold')
    
    # Callout
    plt.annotate('System Saved from Collapse', xy=(8, 500), xytext=(5, 2000),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.title('Admission Control during Pareto Burst', fontweight='bold')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Latency (ms)')
    plt.ylim(0, 3000)
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_23_load_shedding.png")
    plt.close()

def plot_qos_divergence():
    """Slide 24: QoS Divergence"""
    print("Generating QoS Divergence Chart...")
    
    time = np.linspace(0, 20, 200)
    
    # Baseline: Hover around 200
    baseline = 200 + np.random.normal(0, 10, len(time))
    
    # VIP: Drops to 10
    vip = 10 + np.random.normal(0, 2, len(time))
    
    # Standard: Rises to 400
    standard = 200 + (time / 20) * 200 + np.random.normal(0, 10, len(time))
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(time, baseline, label='FIFO (Everyone waits)', color='#95a5a6', linestyle='--', linewidth=2)
    plt.plot(time, vip, label='VIP Traffic', color='#27ae60', linewidth=3)
    plt.plot(time, standard, label='Standard Traffic (Starved)', color='#c0392b', linewidth=3)
    
    # Annotations
    plt.text(18, 20, 'Fast Lane', color='#27ae60', fontweight='bold', ha='right')
    plt.text(18, 420, 'Starvation Penalty', color='#c0392b', fontweight='bold', ha='right')
    
    # Divergence Arrows
    plt.annotate('', xy=(10, 300), xytext=(10, 200), arrowprops=dict(arrowstyle='->', color='black'))
    plt.annotate('', xy=(10, 10), xytext=(10, 200), arrowprops=dict(arrowstyle='->', color='black'))
    
    plt.title('Priority Queuing Analysis', fontweight='bold')
    plt.xlabel('Time (during high load)')
    plt.ylabel('Response Time (ms)')
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/slide_24_qos_divergence.png")
    plt.close()

if __name__ == "__main__":
    plot_work_stealing()
    plot_load_shedding()
    plot_qos_divergence()
    print("Additional charts generated successfully in results/plots/")
