import subprocess
import re
import csv
import os

# --- НАСТРОЙКА ПУТЕЙ ---
# Скрипт лежит в папке с исходниками, а exe-файл лежит в папке сборки.
# Мы строим относительный путь к exe-файлу.
# Если вы переключите конфигурацию в Debug, измените 'x64-Release' на 'x64-Debug' ниже.
EXE_PATH = os.path.join("out", "build", "x64-Release", "mandelbrot.exe")
CSV_FILE = "results.csv"

# Проверка, что файл существует
if not os.path.exists(EXE_PATH):
    print(f"ОШИБКА: Не удалось найти файл {EXE_PATH}")
    print("Убедитесь, что вы собрали проект в конфигурации Release.")
    exit(1)

THREAD_COUNTS = [1, 2, 3, 4, 5, 6, 7, 8]
results = []

print(f"Начинаем тестирование файла: {EXE_PATH}")

for threads in THREAD_COUNTS:
    print(f"Запуск с {threads} потоками...")
    
    try:
        # Запускаем exe и захватываем вывод
        output = subprocess.check_output([EXE_PATH, "-t", str(threads)], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске с {threads} потоками: {e}")
        continue

    # Парсим вывод с помощью регулярных выражений
    serial_match = re.search(r"\[mandelbrot serial\]:\s+\[([\d.]+)\] ms", output)
    thread_match = re.search(r"\[mandelbrot thread\]:\s+\[([\d.]+)\] ms", output)
    speedup_match = re.search(r"\(([\d.]+)x speedup", output)

    if serial_match and thread_match and speedup_match:
        serial_time = float(serial_match.group(1))
        thread_time = float(thread_match.group(1))
        speedup = float(speedup_match.group(1))
        
        results.append({
            "Threads": threads,
            "Serial_Time_ms": serial_time,
            "Thread_Time_ms": thread_time,
            "Speedup": speedup
        })
        print(f"  -> Speedup: {speedup}x")
    else:
        print("  -> Не удалось распарсить вывод программы.")

# Сохраняем результаты в CSV
with open(CSV_FILE, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["Threads", "Serial_Time_ms", "Thread_Time_ms", "Speedup"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nТестирование завершено! Данные сохранены в {CSV_FILE}")