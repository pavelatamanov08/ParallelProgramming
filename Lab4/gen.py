#!/usr/bin/env python3
"""
Генератор матриц для лабораторной работы №4.
Создаёт пары файлов matrix_a_<N>.txt и matrix_b_<N>.txt
для каждого размера N из списка SIZES.
"""

from pathlib import Path
import numpy as np

SIZES     = [200, 400, 800, 1200, 1600, 2000]
SEED      = 42
MIN_VALUE = 0
MAX_VALUE = 9


def generate_matrix(size, rng):
    return rng.integers(MIN_VALUE, MAX_VALUE + 1,
                        size=(size, size), dtype=np.int64)


def save_matrix(matrix, filename):
    with filename.open("w", encoding="utf-8") as file:
        file.write(f"{matrix.shape[0]}\n")
        for row in matrix:
            file.write(" ".join(str(int(v)) for v in row) + "\n")


def main():
    root = Path(__file__).resolve().parent
    rng = np.random.default_rng(SEED)

    for size in SIZES:
        a = generate_matrix(size, rng)
        b = generate_matrix(size, rng)
        save_matrix(a, root / f"matrix_a_{size}.txt")
        save_matrix(b, root / f"matrix_b_{size}.txt")
        print(f"Generated {size}x{size}")


if __name__ == "__main__":
    main()