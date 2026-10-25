#include <stdio.h>
#include <thread>

#include "CycleTimer.h"

typedef struct {
    float x0, x1;
    float y0, y1;
    unsigned int width;
    unsigned int height;
    int maxIterations;
    int* output;
    int threadId;
    int numThreads;
} WorkerArgs;


extern void mandelbrotSerial(
    float x0, float y0, float x1, float y1,
    int width, int height,
    int startRow, int numRows,
    int maxIterations,
    int output[]);

void workerThreadStart(WorkerArgs* const args) {
    // Засекаем время (для проверки, что нагрузка стала равномерной)
    double startTime = CycleTimer::currentSeconds();

    // Чередование строк (Round-Robin)
    // Поток 0 берет строки 0, 3, 6, 9... (для 3 потоков)
    // Поток 1 берет строки 1, 4, 7, 10...
    for (int j = args->threadId; j < args->height; j += args->numThreads) {
        mandelbrotSerial(args->x0, args->y0, args->x1, args->y1,
            args->width, args->height,
            j, 1, // startRow = j, totalRows = 1 (считаем одну строку)
            args->maxIterations, args->output);
    }

    // Засекаем время окончания
    double endTime = CycleTimer::currentSeconds();
    // Раскомментируйте строку ниже, чтобы убедиться, что время потоков сравнялось
    // printf("Thread %d finished in %.3f ms\n", args->threadId, (endTime - startTime) * 1000);
}

void mandelbrotThread(
    int numThreads,
    float x0, float y0, float x1, float y1,
    int width, int height,
    int maxIterations, int output[])
{
    static constexpr int MAX_THREADS = 32;

    if (numThreads > MAX_THREADS)
    {
        fprintf(stderr, "Error: Max allowed threads is %d\n", MAX_THREADS);
        exit(1);
    }

    std::thread workers[MAX_THREADS];
    WorkerArgs args[MAX_THREADS];

    for (int i=0; i<numThreads; i++) {

        args[i].x0 = x0;
        args[i].y0 = y0;
        args[i].x1 = x1;
        args[i].y1 = y1;
        args[i].width = width;
        args[i].height = height;
        args[i].maxIterations = maxIterations;
        args[i].numThreads = numThreads;
        args[i].output = output;
      
        args[i].threadId = i;
    }

    for (int i=1; i<numThreads; i++) {
        workers[i] = std::thread(workerThreadStart, &args[i]);
    }
    
    workerThreadStart(&args[0]);


    for (int i=1; i<numThreads; i++) {
        workers[i].join();
    }
}

