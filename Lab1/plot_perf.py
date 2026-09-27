from pathlib import Path
import csv
import matplotlib.pyplot as plt

def main():
    root = Path(__file__).resolve().parent
    csv_file = root / "benchmark.csv"

    if not csv_file.exists():
        print("benchmark.csv not found. Run the C++ program first.")
        return 1

    sizes, seq, par, speedup = [], [], [], []
    with csv_file.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sizes.append(int(row["matrix_size"]))
            seq.append(float(row["sequential_ms"]))
            par.append(float(row["parallel_ms"]))
            speedup.append(float(row["speedup"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(sizes, seq, "o-", label="Sequential")
    ax1.plot(sizes, par, "s-", label="Parallel")
    ax1.set_xlabel("Matrix size N")
    ax1.set_ylabel("Time (ms)")
    ax1.set_title("Time vs N")
    ax1.legend()
    ax1.grid(True)

    ax2.plot(sizes, speedup, "^-", color="green")
    ax2.axhline(y=1, color="gray", linestyle="--")
    ax2.set_xlabel("Matrix size N")
    ax2.set_ylabel("Speedup")
    ax2.set_title("Speedup vs N")
    ax2.grid(True)

    plt.tight_layout()
    out = root / "performance.png"
    plt.savefig(out, dpi=120)
    print(f"Saved: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())