#!/usr/bin/env python3
import csv
import subprocess
import sys
import time
from pathlib import Path

SIZES        = [200, 400, 800, 1200, 1600, 2000]
BLOCKS       = [8, 16, 32]
BINARY_NAME  = "Lab4"
BENCHMARK_CSV = "benchmark.csv"

ROOT       = Path(__file__).resolve().parent
BUILD_DIR  = ROOT / "build"


def run(cmd, cwd=None, check=True, capture=False):
    print(f"$ {' '.join(map(str, cmd))}")
    result = subprocess.run(
        cmd, cwd=cwd, check=False, capture_output=capture, text=True,
    )
    if check and result.returncode != 0:
        if capture:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed with code {result.returncode}: {cmd}")
    return result


def find_binary():
    candidates = [
        ROOT / "out" / "build" / "x64-Release" / (BINARY_NAME + ".exe"),
        ROOT / "out" / "build" / "x64-Debug"   / (BINARY_NAME + ".exe"),
        ROOT / "out" / "build" / "x64-Release" / BINARY_NAME,
        ROOT / "out" / "build" / "x64-Debug"   / BINARY_NAME,
        BUILD_DIR / BINARY_NAME,
        BUILD_DIR / (BINARY_NAME + ".exe"),
        BUILD_DIR / "Release" / (BINARY_NAME + ".exe"),
        BUILD_DIR / "Debug"   / (BINARY_NAME + ".exe"),
        ROOT / BINARY_NAME,
        ROOT / (BINARY_NAME + ".exe"),
    ]

    print("Looking for binary in:")
    for c in candidates:
        exists = c.exists()
        print(f"  {c}  {'<-- FOUND' if exists else ''}")
        if exists:
            return c

    raise FileNotFoundError(
        f"Binary '{BINARY_NAME}' not found.\n"
        f"Build the project first (in Visual Studio: Build → Build All)."
    )


def build_project():
    print("\n=== Build ===")
    BUILD_DIR.mkdir(exist_ok=True)
    run(["cmake", ".."], cwd=BUILD_DIR)
    run(["cmake", "--build", ".", "--config", "Release"], cwd=BUILD_DIR)


def generate_matrices():
    print("\n=== Generate matrices ===")
    run([sys.executable, "gen.py"], cwd=ROOT)

def parse_output(stdout: str):
    """
    Ожидает строки:
        Matrix size:  200
        Block size:   16 x 16
        CPU time:     5.0862 ms
        GPU time:     0.3421 ms
        Result check: OK (maxDiff = 0)
        Speedup:      14.87
    """
    data = {}
    for raw in stdout.splitlines():
        line = raw.strip()
        if line.startswith("Matrix size:"):
            data["size"] = int(line.split(":")[1].strip())
        elif line.startswith("Block size:"):
            data["block"] = int(line.split(":")[1].strip().split()[0])
        elif line.startswith("CPU time:"):
            data["cpu_ms"] = float(line.split(":")[1].strip().split()[0])
        elif line.startswith("GPU time:"):
            data["gpu_ms"] = float(line.split(":")[1].strip().split()[0])
        elif line.startswith("Speedup:"):
            data["speedup"] = float(line.split(":")[1].strip())
        elif line.startswith("Result check:"):
            data["check"] = "OK" if " OK" in line else "FAILED"

    required = {"size", "block", "cpu_ms", "gpu_ms", "speedup", "check"}
    if not required.issubset(data.keys()):
        return None
    return data


def run_experiment(binary: Path, size: int, block: int):
    file_a = f"matrix_a_{size}.txt"
    file_b = f"matrix_b_{size}.txt"

    if not (ROOT / file_a).exists() or not (ROOT / file_b).exists():
        print(f"  ! Skipping: missing {file_a} / {file_b}")
        return None

    try:
        result = run(
            [str(binary), file_a, file_b, str(block)],
            cwd=ROOT, capture=True, check=False,
        )
    except Exception as e:
        print(f"  ! Launch error: {e}")
        return None

    if result.returncode not in (0, 2):
        print(f"  ! Non-zero exit code: {result.returncode}")
        print(result.stderr)
        return None

    parsed = parse_output(result.stdout)
    if parsed is None:
        print("  ! Could not parse output:")
        print(result.stdout)
        return None

    return parsed


def verify_result(size: int):
    print(f"\n=== Verify result.txt (reference size n={size}) ===")
    verify_script = ROOT / "verify.py"
    if not verify_script.exists():
        print("  ! verify.py not found, skipping.")
        return
    run([sys.executable, "verify.py", str(size)], cwd=ROOT, check=False)


def write_benchmark(rows):
    csv_path = ROOT / BENCHMARK_CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "matrix_size", "block_size",
            "cpu_ms", "gpu_ms", "speedup", "check",
        ])
        for r in rows:
            writer.writerow([
                r["size"], r["block"],
                f"{r['cpu_ms']:.4f}",
                f"{r['gpu_ms']:.4f}",
                f"{r['speedup']:.4f}",
                r["check"],
            ])
    print(f"\nBenchmark saved: {csv_path}")


def print_summary(rows):
    print("\n=== Summary ===")
    header = (f"{'n':>6} {'block':>6} "
              f"{'cpu_ms':>12} {'gpu_ms':>12} {'speedup':>10} {'check':>8}")
    print(header)
    print("-" * len(header))
    for r in rows:
        blk = f"{r['block']}x{r['block']}"
        print(f"{r['size']:>6} {blk:>6} "
              f"{r['cpu_ms']:>12.4f} {r['gpu_ms']:>12.4f} "
              f"{r['speedup']:>10.4f} {r['check']:>8}")


def plot_results(rows):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — skipping plot.")
        return

    from collections import defaultdict
    by_block = defaultdict(list)
    for r in rows:
        by_block[r["block"]].append((r["size"], r["speedup"]))

    plt.figure(figsize=(9, 6))
    for block, pts in sorted(by_block.items()):
        pts.sort()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        plt.plot(xs, ys, marker="o", label=f"block {block}x{block}")

    plt.xlabel("Matrix size n")
    plt.ylabel("Speedup (CPU / GPU)")
    plt.title("CUDA matrix multiplication speedup")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    out = ROOT / "speedup.png"
    plt.savefig(out, dpi=150)
    print(f"Plot saved: {out}")


def main():
    overall_start = time.time()

    generate_matrices()

    binary = find_binary()
    print(f"\nUsing binary: {binary}")

    all_rows = []
    last_size = SIZES[-1]

    print("\n=== Running experiments ===")
    for size in SIZES:
        print(f"\n--- Matrix size: {size} ---")
        for block in BLOCKS:
            print(f"  Running: n={size}, block={block}x{block}")
            row = run_experiment(binary, size, block)
            if row is not None:
                all_rows.append(row)
                print(f"    CPU={row['cpu_ms']:.2f} ms, "
                      f"GPU={row['gpu_ms']:.2f} ms, "
                      f"speedup={row['speedup']:.2f}, "
                      f"check={row['check']}")

    if not all_rows:
        print("\n!!! No successful runs. Check build and GPU availability.")
        sys.exit(1)

    write_benchmark(all_rows)
    print_summary(all_rows)
    plot_results(all_rows)
    verify_result(last_size)

    elapsed = time.time() - overall_start
    print(f"\nAll experiments finished in {elapsed:.1f} s.")
    print(f"Total runs: {len(all_rows)}")


if __name__ == "__main__":
    main()