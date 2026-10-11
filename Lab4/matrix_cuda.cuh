#ifndef MATRIX_CUDA_H
#define MATRIX_CUDA_H

#include "matrix.h"

double multiplyCuda(const Matrix& a, const Matrix& b, Matrix& result, int blockSize);

#endif // MATRIX_CUDA_H