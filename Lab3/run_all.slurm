#!/bin/bash
#SBATCH --job-name=Lab3_All
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=all_experiments_%j.out

# Загружаем модули
module load intel/icc18
module load intel/mpi4

# Список размеров и ядер
SIZES="200 400 800 1200 1600 2000"
PROCS="1 2 4 8"

for N in $SIZES; do
    echo "=== Размер матрицы: $N x $N ==="
    
    # Копируем нужные матрицы в рабочую директорию
    cp matrices_$N/matrix_a.txt .
    cp matrices_$N/matrix_b.txt .
    
    for P in $PROCS; do
        echo "  -> Запуск на $P процессах..."
        
        # Вместо отправки в очередь, запускаем напрямую через srun
        # Так как мы уже внутри выделенного задания Slurm
        srun -n $P ./Lab3
        
        echo "  ---------------------------------"
    done
done

echo "Все эксперименты завершены!"
