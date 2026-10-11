#include <iostream>
#include <chrono>
#include <cmath>
#include <string>

#include "matrix.h"
#include "matrix_io.h"
#include "matrix_cpu.h"
#include "matrix_cuda.cuh"

namespace {

double maxDiff(const Matrix& x, const Matrix& y) {
    double m = 0.0;
    for (std::size_t i = 0; i < x.size(); ++i) {
        for (std::size_t j = 0; j < x.size(); ++j) {
            m = std::max(m, std::abs(x(i, j) - y(i, j)));
        }
    }
    return m;
}

}

int main(int argc, char** argv) {
    try {
        if (argc < 4) {
            std::cerr << "Usage: " << argv[0]
                      << " <matrix_a> <matrix_b> <block_size>\n";
            std::cerr << "Example: " << argv[0]
                      << " matrix_a_200.txt matrix_b_200.txt 16\n";
            return 1;
        }

        const std::string fileA = argv[1];
        const std::string fileB = argv[2];
        const int blockSize = std::stoi(argv[3]);

        const Matrix a = readMatrix(fileA);
        const Matrix b = readMatrix(fileB);

        if (a.size() != b.size()) {
            std::cerr << "Matrix size mismatch!\n";
            return 1;
        }

        const std::size_t n = a.size();

        std::cout << "Matrix size:  " << n << "\n";
        std::cout << "Block size:   " << blockSize << " x " << blockSize << "\n";

        const auto cpuStart = std::chrono::steady_clock::now();
        const Matrix cpuResult = multiplySequential(a, b);
        const auto cpuEnd = std::chrono::steady_clock::now();
        const double cpuMs =
            std::chrono::duration<double, std::milli>(cpuEnd - cpuStart).count();

        std::cout << "CPU time:     " << cpuMs << " ms\n";

        Matrix gpuResult(n);
        const double gpuMs = multiplyCuda(a, b, gpuResult, blockSize);
        std::cout << "GPU time:     " << gpuMs << " ms\n";

        const double diff = maxDiff(cpuResult, gpuResult);
        const bool correct = diff < 1e-6;
        std::cout << "Result check: " << (correct ? "OK" : "FAILED")
                  << " (maxDiff = " << diff << ")\n";

        const double speedup = (gpuMs > 0.0) ? cpuMs / gpuMs : 0.0;
        std::cout << "Speedup:      " << speedup << "\n";

        writeMatrix(gpuResult, "result.txt");
        appendBenchmark("benchmark.csv", n, blockSize, cpuMs, gpuMs);

        std::cout << "\nResult:    result.txt\n";
        std::cout << "Benchmark: benchmark.csv\n";

        return correct ? 0 : 2;
    }
    catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n";
        return 1;
    }
}