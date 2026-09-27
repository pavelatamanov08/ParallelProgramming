from pathlib import Path
import numpy as np

SIZE = 500
SEED = 42
MIN_VALUE = 0
MAX_VALUE = 9

def generate_matrix(size, rng):
    return rng.integers(MIN_VALUE, MAX_VALUE + 1, size=(size, size), dtype=np.int64)

def save_matrix(matrix, filename):
    with filename.open("w", encoding="utf-8") as file:
        file.write(f"{matrix.shape[0]}\n")
        for row in matrix:
            file.write(" ".join(str(int(v)) for v in row) + "\n")

def main():
    root = Path(__file__).resolve().parent
    rng = np.random.default_rng(SEED)

    a = generate_matrix(SIZE, rng)
    b = generate_matrix(SIZE, rng)

    save_matrix(a, root / "matrix_a.txt")
    save_matrix(b, root / "matrix_b.txt")

    print(f"Generated {SIZE}x{SIZE} matrices")
    print(f"  {root / 'matrix_a.txt'}")
    print(f"  {root / 'matrix_b.txt'}")

if __name__ == "__main__":
    main()