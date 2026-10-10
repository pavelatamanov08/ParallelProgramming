export module matrix_multiply;

import std;
import matrix;

extern "C" {
    void omp_set_num_threads(int num_threads);
}

export Matrix multiplySequential(const Matrix& a, const Matrix& b)
{
    std::size_t n = a.size();
    Matrix result(n);

    for (std::size_t i = 0; i < n; ++i)
    {
        for (std::size_t k = 0; k < n; ++k)
        {
            double aik = a(i, k);
            for (std::size_t j = 0; j < n; ++j)
            {
                result(i, j) += aik * b(k, j);
            }
        }
    }
    return result;
}

export Matrix multiplyParallel(const Matrix& a, const Matrix& b, int numThreads)
{
    std::size_t n = a.size();
    Matrix result(n);

    omp_set_num_threads(numThreads);

#pragma omp parallel for
    for (int i = 0; i < static_cast<int>(n); ++i)
    {
        for (std::size_t k = 0; k < n; ++k)
        {
            double aik = a(i, k);
            for (std::size_t j = 0; j < n; ++j)
            {
                result(i, j) += aik * b(k, j);
            }
        }
    }
    return result;
}