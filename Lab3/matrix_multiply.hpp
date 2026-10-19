#pragma once

#include <cstddef>
#include "matrix.hpp"

Matrix multiplySequential(const Matrix& a, const Matrix& b);
Matrix multiplyMPI(const Matrix& a, const Matrix& b);