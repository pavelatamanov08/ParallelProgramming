import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("benchmark.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

for size in sorted(df['matrix_size'].unique()):
    data = df[df['matrix_size'] == size]
    ax1.plot(data['threads'], data['parallel_ms'], marker='o', label=f'Size {size}')

ax1.set_xlabel('Количество потоков')
ax1.set_ylabel('Время выполнения (мс)')
ax1.set_title('Зависимость времени от количества потоков')
ax1.legend()
ax1.grid(True)

for size in sorted(df['matrix_size'].unique()):
    data = df[df['matrix_size'] == size]
    ax2.plot(data['threads'], data['speedup'], marker='o', label=f'Size {size}')

ax2.set_xlabel('Количество потоков')
ax2.set_ylabel('Ускорение (Speedup)')
ax2.set_title('Зависимость ускорения от количества потоков')
ax2.axhline(y=1, color='r', linestyle='--', label='Без ускорения')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('performance.png')
plt.show()