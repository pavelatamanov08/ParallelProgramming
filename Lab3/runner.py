#!/usr/bin/env python3
"""
Автозапуск лабораторной №3 (Sequential + MPI).
Работает с проектом, открытым в Visual Studio как папка (out/build/<config>/).
Запуск: python runner.py (или py runner.py)
"""

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SIZES = [200, 400, 800, 1200, 1600, 2000]
PROCS = [1, 2, 4, 8]

EXE_CANDIDATES = [
    "out/build/x64-Release/Lab3.exe",
    "out/build/x64-Debug/Lab3.exe",
    "out/build/x64-release/Lab3.exe",
    "out/build/x64-debug/Lab3.exe",
    "out/build/Release/Lab3.exe",
    "out/build/Debug/Lab3.exe",
    "out/build/Lab3.exe",
    "Lab3.exe", "Lab3",
]

def find_exe(root: Path):
    for rel in EXE_CANDIDATES:
        p = root / rel
        if p.exists():
            return p
    return None


def sh(cmd, cwd=None, capture=True, check=True):
    print(f"  $ {' '.join(str(x) for x in cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check,
                          capture_output=capture, text=True)


def build_if_needed(root: Path) -> Path:
    """Если exe нет — пробует собрать через cmake --build out/build/<config>."""
    exe = find_exe(root)
    if exe is not None:
        print(f"[BUILD] Уже собрано: {exe}")
        return exe

    out_build = root / "out" / "build"
    if not out_build.exists():
        raise RuntimeError(
            "Нет папки out/build. Откройте проект в Visual Studio "
            "(File → Open → Folder) и соберите его один раз."
        )

    configs = sorted(
        [d.name for d in out_build.iterdir()
         if d.is_dir() and not d.name.startswith(".")],
        key=lambda n: (0 if "release" in n.lower() else 1, n)
    )

    for cfg in configs:
        cfg_dir = out_build / cfg
        if not (cfg_dir / "CMakeCache.txt").exists():
            continue
        cmake_config = "Release" if "release" in cfg.lower() else "Debug"
        print(f"[BUILD] cmake --build {cfg_dir} --config {cmake_config}")
        sh(["cmake", "--build", str(cfg_dir), "--config", cmake_config],
           cwd=root)
        exe = find_exe(root)
        if exe is not None:
            return exe

    raise RuntimeError("Не нашли собранный Lab3.exe в out/build/")


def generate_matrix(root: Path, size: int) -> None:
    """Подменяет SIZE в gen.py через временный файл и запускает его."""
    gen_script = root / "gen.py"
    if not gen_script.exists():
        raise FileNotFoundError("gen.py не найден рядом с runner.py")

    for name in ("matrix_a.txt", "matrix_b.txt"):
        (root / name).unlink(missing_ok=True)

    src = gen_script.read_text(encoding="utf-8")
    patched = re.sub(r"^SIZE\s*=\s*\d+", f"SIZE = {size}", src,
                     flags=re.MULTILINE)
    tmp = root / f"_gen_{size}.py"
    tmp.write_text(patched, encoding="utf-8")
    try:
        sh([sys.executable, str(tmp)], cwd=root)
    finally:
        tmp.unlink(missing_ok=True)


def sync_matrices(root: Path, run_cwd: Path) -> None:
    """Копирует свежие матрицы туда, откуда их читает Lab3.exe."""
    for name in ("matrix_a.txt", "matrix_b.txt"):
        src = root / name
        if src.exists():
            shutil.copy2(src, run_cwd / name)


def mpi_cmd(procs: int, exe: Path):
    if shutil.which("srun") and "SLURM_JOB_ID" in os.environ:
        return ["srun", "-n", str(procs), str(exe)]
    runner = (shutil.which("mpiexec") or
              shutil.which("mpirun"))
    if runner is None:
        raise RuntimeError("mpiexec/mpirun не найдены в PATH.")
    return [runner, "-np", str(procs), str(exe)]


RE_SEQ       = re.compile(r"Sequential:\s+([\d.]+)\s*ms")
RE_MPI       = re.compile(r"MPI\s*\((\d+)\s*procs?\):\s+([\d.]+)\s*ms")
RE_CHECK_MPI = re.compile(r"MPI vs Sequential:\s+(\w+)")


def parse_output(text: str):
    m = RE_SEQ.search(text)
    if not m:
        return None
    out = {"seq_ms": float(m.group(1))}

    m = RE_MPI.search(text)
    if not m:
        return None
    out["mpi_procs"] = int(m.group(1))
    out["mpi_ms"]    = float(m.group(2))

    m = RE_CHECK_MPI.search(text)
    out["mpi_ok"] = (m.group(1) == "OK") if m else False

    return out

def main() -> int:
    root = Path(__file__).resolve().parent

    print("=" * 60)
    print("Лабораторная №3: Sequential + MPI")
    print(f"Project root: {root}")
    print("=" * 60)

    try:
        exe = build_if_needed(root)
    except Exception as e:
        print(f"ERROR при сборке: {e}")
        return 1

    run_cwd = exe.parent
    print(f"[RUN] cwd: {run_cwd}")

    try:
        mpi_cmd(1, exe)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        return 2

    csv_path = root / "benchmark.csv"
    if csv_path.exists():
        csv_path.unlink()
        print("[CSV] Старый benchmark.csv удалён")

    total  = len(SIZES) * len(PROCS)
    done   = 0
    failed = 0

    for size in SIZES:
        print(f"\n--- N = {size} ---")

        try:
            generate_matrix(root, size)
            time.sleep(1.0)
            sync_matrices(root, run_cwd)
        except Exception as e:
            print(f"  ! ERROR генерации N={size}: {e}")
            failed += len(PROCS)
            continue

        for p in PROCS:
            print(f"\n[{done + 1}/{total}] N={size}, P={p}")
            try:
                res = sh(mpi_cmd(p, exe), cwd=run_cwd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"  ! Программа упала (код {e.returncode})")
                if e.stdout: print(e.stdout)
                if e.stderr: print(e.stderr)
                failed += 1
                continue

            print(res.stdout.rstrip())

            parsed = parse_output(res.stdout)
            if parsed is None:
                print("  ! Не удалось распарсить вывод")
                failed += 1
                continue

            if not parsed.get("mpi_ok"):
                print("  ! Проверка корректности MPI не пройдена")

            mpi_ms = parsed["mpi_ms"]
            mpi_sp = (parsed["seq_ms"] / mpi_ms) if mpi_ms > 0 else 0.0

            with csv_path.open("a", encoding="utf-8") as f:
                if csv_path.stat().st_size == 0:
                    f.write("matrix_size,sequential_ms,mpi_ms,"
                            "mpi_speedup,mpi_procs\n")
                f.write(f"{size},{parsed['seq_ms']:.6f},"
                        f"{mpi_ms:.6f},{mpi_sp:.6f},{p}\n")

            done += 1

    print("\n" + "=" * 60)
    print(f"Успешных прогонов: {done} / {total}  (ошибок: {failed})")
    print(f"CSV: {csv_path}")

    plot_script = root / "plot_perf.py"
    if plot_script.exists() and done > 0:
        print("\n[PLOT] Строю графики...")
        try:
            sh([sys.executable, str(plot_script)], cwd=root)
        except subprocess.CalledProcessError as e:
            print(f"  ! plot_perf.py упал: {e}")
            return 4

    return 0 if failed == 0 else 3


if __name__ == "__main__":
    sys.exit(main())