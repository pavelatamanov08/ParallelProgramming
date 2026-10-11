#include "matrix_io.h"

#include <fstream>
#include <iostream>
#include <stdexcept>

Matrix readMatrix(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    }

    std::size_t size;
    file >> size;
    if (file.fail() || size == 0) {
        throw std::runtime_error("Invalid matrix size in file: " + filename);
    }

    Matrix matrix(size);
    for (std::size_t i = 0; i < size; ++i) {
        for (std::size_t j = 0; j < size; ++j) {
            file >> matrix(i, j);
            if (file.fail()) {
                throw std::runtime_error("Error reading matrix data from " + filename);
            }
        }
    }
    return matrix;
}

void writeMatrix(const Matrix& matrix, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file for writing: " + filename);
    }

    file << matrix.size() << "\n";
    for (std::size_t i = 0; i < matrix.size(); ++i) {
        for (std::size_t j = 0; j < matrix.size(); ++j) {
            file << matrix(i, j) << (j == matrix.size() - 1 ? "" : " ");
        }
        file << "\n";
    }
}

void appendBenchmark(const std::string& filename,
    std::size_t size,
    int blockSize,
    double cpuMs,
    double gpuMs) {
    std::ofstream file;
    bool writeHeader = false;
    {
        std::ifstream check(filename);
        if (!check.good()) writeHeader = true;
    }

    file.open(filename, std::ios::app);
    if (!file.is_open()) return;

    if (writeHeader) {
        file << "matrix_size,block_size,cpu_ms,gpu_ms,speedup\n";
    }

    double speedup = (gpuMs > 0.0) ? (cpuMs / gpuMs) : 0.0;
    file << size << "," << blockSize << ","
        << cpuMs << "," << gpuMs << "," << speedup << "\n";
}