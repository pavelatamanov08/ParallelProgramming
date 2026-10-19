from pathlib import Path
import csv
import matplotlib.pyplot as plt
from collections import defaultdict

def main():
    root = Path(__file__).resolve().parent
    csv_file = root / "benchmark.csv"

    if not csv_file.exists():
        print("benchmark.csv not found. Run the C++ program first.")
        return 1

    data = defaultdict(dict)
    
    with csv_file.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n = int(row["matrix_size"])
            p = int(row["mpi_procs"])
            seq = float(row["sequential_ms"])
            mpi = float(row["mpi_ms"])

            if mpi > 0 and seq > 0:
                data[n][p] = (seq, mpi)

    if not data:
        print("No valid data found.")
        return 1

    sizes = sorted(data.keys())
    proc_counts = sorted({p for n in data for p in data[n]})

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    colors = plt.cm.viridis([i / max(1, len(proc_counts)-1) for i in range(len(proc_counts))])

    seq_times = [data[n][next(iter(data[n]))][0] for n in sizes]

    ax1.plot(sizes, seq_times, "k--.", label="Sequential", linewidth=2, markersize=8)

    for i, p in enumerate(proc_counts):
        mpi_times = [data[n].get(p, (0, 0))[1] for n in sizes]
        ax1.plot(sizes, mpi_times, ".-", color=colors[i], label=f"MPI ({p} procs)", markersize=8)

    ax1.set_xlabel("Matrix size N")
    ax1.set_ylabel("Time (ms)")
    ax1.set_title("1. Execution time vs N")
    ax1.legend()
    ax1.grid(True)

    for i, p in enumerate(proc_counts):
        speedups = []
        for n in sizes:
            if p in data[n]:
                seq, mpi = data[n][p]
                speedups.append(seq / mpi)
            else:
                speedups.append(None)

        ax2.plot(sizes, speedups, ".-", color=colors[i], label=f"Speedup ({p} procs)", markersize=8)

    ax2.axhline(y=1, color="red", linestyle=":", alpha=0.5, label="Baseline (1x)")
    ax2.set_xlabel("Matrix size N")
    ax2.set_ylabel("Speedup")
    ax2.set_title("2. Speedup vs N")
    ax2.legend()
    ax2.grid(True)

    colors_n = plt.cm.plasma([i / max(1, len(sizes)-1) for i in range(len(sizes))])
    
    for i, n in enumerate(sizes):
        procs_available = sorted(data[n].keys())
        mpi_times = [data[n][p][1] for p in procs_available]

        ax3.plot(procs_available, mpi_times, ".-", color=colors_n[i], label=f"N={n}", markersize=6)

    ax3.set_xlabel("MPI processes")
    ax3.set_ylabel("MPI time (ms)")
    ax3.set_title("3. MPI time vs #processes")
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout()
    
    out = root / "performance.png"
    plt.savefig(out, dpi=150)
    print(f"Saved: {out}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())