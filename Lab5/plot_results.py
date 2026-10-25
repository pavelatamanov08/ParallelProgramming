import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_FILE = "results.csv"

# Читаем данные из CSV
if not os.path.exists(CSV_FILE):
    print(f"Ошибка: Файл {CSV_FILE} не найден. Сначала запустите run_tests.py")
    exit()

df = pd.read_csv(CSV_FILE)

# Настраиваем график
plt.figure(figsize=(10, 6))

# Строим наш график ускорения
plt.plot(df['Threads'], df['Speedup'], marker='o', label='Фактическое ускорение', color='blue', linewidth=2, markersize=8)

# Строим линию идеального ускорения (y = x)
plt.plot(df['Threads'], df['Threads'], linestyle='--', label='Идеальное линейное ускорение', color='red', alpha=0.7)

# Добавляем подписи и заголовок
plt.title('Speedup фрактала Мандельброта (Метод Round-Robin)', fontsize=14)
plt.xlabel('Количество потоков', fontsize=12)
plt.ylabel('Ускорение (Speedup)', fontsize=12)
plt.xticks(df['Threads'])
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# --- БЛОК С АННОТАЦИЕЙ УДАЛЕН ---

# Сохраняем график в файл
plt.tight_layout()
plt.savefig("speedup_plot.png", dpi=300)
print("График сохранен в файл speedup_plot.png")

# Показываем график на экране
plt.show()