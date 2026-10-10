import subprocess
import os
import sys

SIZES = [200, 400, 800, 1200, 1600, 2000]
THREADS = [1, 2, 4, 8]

EXE_PATH = "out/build/x64-Release/Lab2.exe" 

if not os.path.exists(EXE_PATH):
    print(f"Ошибка: Не найден {EXE_PATH}. Сначала соберите проект в Visual Studio.")
    sys.exit(1)

if os.path.exists("benchmark.csv"):
    os.remove("benchmark.csv")

for size in SIZES:
    print(f"\n--- Генерация матриц размера {size} ---")
    subprocess.run([sys.executable, "gen.py", str(size)], check=True)
    
    for t in THREADS:
        print(f"Запуск: size={size}, threads={t}...")
        subprocess.run([EXE_PATH, str(size), str(t)], check=True)

print("\nВсе эксперименты завершены. Проверьте benchmark.csv")