#ifndef MATRIX_IO_H
#define MATRIX_IO_H

#include "matrix.h"
#include <string>

Matrix readMatrix(const std::string& filename);
void writeMatrix(const Matrix& matrix, const std::string& filename);

void appendBenchmark(const std::string& filename,
                     std::size_t size,
                     int blockSize,
                     double cpuMs,
                     double gpuMs);

#endif // MATRIX_IO_H