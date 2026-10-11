#include "matrix_cpu.h"

#include <stdexcept>

Matrix multiplySequential(const Matrix& a, const Matrix& b) {
    if (a.size() != b.size()) {
        throw std::invalid_argument("Matrix dimensions must match.");
    }

    std::size_t n = a.size();
    Matrix result(n);

    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            double sum = 0.0;
            for (std::size_t k = 0; k < n; ++k) {
                sum += a(i, k) * b(k, j);
            }
            result(i, j) = sum;
        }
    }
    return result;
}