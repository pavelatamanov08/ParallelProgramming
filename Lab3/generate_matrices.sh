#!/bin/bash

SIZES="200 400 800 1200 1600 2000"

for N in $SIZES; do
    echo "Генерация матриц размера $N x $N..."
    mkdir -p matrices_$N
    
    # Генерируем случайные числа от 0 до 9 с помощью awk
    awk -v n=$N 'BEGIN {
        srand();
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++) {
                printf("%d ", int(rand() * 10));
            }
            printf("\n");
        }
    }' > matrices_$N/matrix_a.txt

    awk -v n=$N 'BEGIN {
        srand();
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++) {
                printf("%d ", int(rand() * 10));
            }
            printf("\n");
        }
    }' > matrices_$N/matrix_b.txt

    # Добавляем размер в начало файла (как требует ваша программа)
    for f in matrices_$N/matrix_a.txt matrices_$N/matrix_b.txt; do
        sed -i "1i $N" $f
    done
done

echo "Все матрицы сгенерированы!"
