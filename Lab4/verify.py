#!/usr/bin/env python3
"""
Автоматизированная верификация результата умножения матриц.
Сравнивает result.txt (полученный программой Lab4) с эталоном NumPy.

Использование:
    python3 verify.py <size>
"""

import sys
from pathlib import Path
import numpy as np


def read_matrix(filename):
    path = Path(filename)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return None
        size = int(lines[0].strip())
        matrix = np.zeros((size, size), dtype=np.int64)
        for i in range(size):
            matrix[i] = list(map(int, lines[i + 1].split()))
    return matrix


def verify(size):
    a = read_matrix(f"matrix_a_{size}.txt")
    b = read_matrix(f"matrix_b_{size}.txt")
    result_cpp = read_matrix("result.txt")

    if a is None or b is None or result_cpp is None:
        print(f"Size {size}: ERROR — missing input or result files.")
        return False

    if a.shape != b.shape or a.shape != result_cpp.shape:
        print(f"Size {size}: ERROR — shape mismatch.")
        return False

    print(f"Size {size}: computing reference with NumPy...")
    expected = np.dot(a, b)

    if np.array_equal(expected, result_cpp):
        print(f"Size {size}: SUCCESS — C++ result matches NumPy.")
        return True

    diff_indices = np.where(expected != result_cpp)
    n_diff = len(diff_indices[0])
    print(f"Size {size}: FAILURE — {n_diff} mismatched elements.")
    if n_diff > 0:
        i, j = diff_indices[0][0], diff_indices[1][0]
        print(f"  Example at ({i},{j}): expected {expected[i,j]}, got {result_cpp[i,j]}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify.py <size>")
        sys.exit(1)
    ok = verify(int(sys.argv[1]))
    sys.exit(0 if ok else 1)