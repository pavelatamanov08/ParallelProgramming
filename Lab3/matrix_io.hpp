#pragma once

#include <cstddef>
#include <string>
#include "matrix.hpp"

Matrix readMatrix(const std::string& filename);

void writeMatrix(const Matrix& matrix, const std::string& filename);

void appendBenchmark(const std::string& filename,
    std::size_t matrixSize,
    double sequentialMs,
    double mpiMs,
    std::size_t mpiProcs);