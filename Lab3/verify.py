from pathlib import Path
import subprocess
import sys
import numpy as np

def read_matrix(filename):
    with filename.open("r", encoding="utf-8") as file:
        size = int(file.readline())
        values = []
        for line in file:
            values.extend(float(v) for v in line.split())
    if len(values) != size * size:
        raise ValueError(f"{filename}: expected {size*size} values, got {len(values)}")
    return np.array(values, dtype=np.float64).reshape(size, size)

def find_executable(root):
    candidates = [
        root / "Lab3.exe",
        root / "Lab3",
        root / "build" / "Lab3.exe",
        root / "build" / "Lab3",
        root / "build" / "Release" / "Lab3.exe",
        root / "build" / "Debug" / "Lab3.exe",
    ]
    return next((p for p in candidates if p.exists()), None)

def main():
    root = Path(__file__).resolve().parent

    exe = find_executable(root)
    if exe is None:
        print("ERROR: Lab3 executable not found. Build first (cmake --build build).")
        return 1

    if not (root / "matrix_a.txt").exists() or not (root / "matrix_b.txt").exists():
        print("ERROR: matrix_a.txt / matrix_b.txt not found. Run gen.py first.")
        return 1

    result_file = root / "result.txt"
    if result_file.exists():
        result_file.unlink()

    # Запускаем через mpirun, чтобы проверить именно MPI-режим
    # (можно и напрямую — тогда MPI запустится в 1 процесс)
    cmd = ["mpirun", "-np", "4", str(exe)]
    print("Running:", " ".join(cmd))
    process = subprocess.run(cmd, cwd=root, text=True)

    if process.returncode != 0:
        print(f"C++ program exited with code {process.returncode}")
        return process.returncode

    a = read_matrix(root / "matrix_a.txt")
    b = read_matrix(root / "matrix_b.txt")
    cpp = read_matrix(root / "result.txt")
    ref = a @ b

    diff = np.max(np.abs(cpp - ref))
    print()
    print("Python / NumPy verification")
    print("---------------------------")
    print(f"Maximum absolute difference: {diff:.3e}")

    if np.allclose(cpp, ref, rtol=1e-9, atol=1e-9):
        print("RESULT: OK")
        return 0

    print("RESULT: FAILED")
    return 2

if __name__ == "__main__":
    sys.exit(main())