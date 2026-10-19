#include <mpi.h>
#include "matrix_multiply.hpp"
#include "mpi_utils.hpp"

#include <vector>
#include <stdexcept>

Matrix multiplySequential(const Matrix& a, const Matrix& b) {
    if (a.size() != b.size()) {
        throw std::invalid_argument("Matrix sizes must be equal.");
    }
    const std::size_t n = a.size();
    Matrix result(n);

    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t k = 0; k < n; ++k) {
            const double value = a(i, k);
            for (std::size_t j = 0; j < n; ++j) {
                result(i, j) += value * b(k, j);
            }
        }
    }
    return result;
}

Matrix multiplyMPI(const Matrix& a, const Matrix& b) {
    const int rank = getRank();
    const int size = getSize();
    const std::size_t n = a.size();

    Matrix result(n);

    MPI_Bcast(const_cast<double*>(b.data()),
        static_cast<int>(n * n),
        MPI_DOUBLE, 0, MPI_COMM_WORLD);

    std::vector<int> sendcounts(size), displs(size);
    const std::size_t rowsPerProc = n / static_cast<std::size_t>(size);
    const std::size_t extra = n % static_cast<std::size_t>(size);
    int offset = 0;
    for (int i = 0; i < size; ++i) {
        const std::size_t rows =
            rowsPerProc + (static_cast<std::size_t>(i) < extra ? 1 : 0);
        sendcounts[i] = static_cast<int>(rows * n);
        displs[i] = offset;
        offset += sendcounts[i];
    }

    std::vector<double> localA(sendcounts[rank]);
    MPI_Scatterv(const_cast<double*>(a.data()),
        sendcounts.data(), displs.data(), MPI_DOUBLE,
        localA.data(), sendcounts[rank], MPI_DOUBLE,
        0, MPI_COMM_WORLD);

    const std::size_t localRows =
        static_cast<std::size_t>(sendcounts[rank]) / n;
    std::vector<double> localC(localRows * n, 0.0);

    for (std::size_t i = 0; i < localRows; ++i) {
        for (std::size_t k = 0; k < n; ++k) {
            const double v = localA[i * n + k];
            for (std::size_t j = 0; j < n; ++j) {
                localC[i * n + j] += v * b(k, j);
            }
        }
    }

    MPI_Gatherv(localC.data(), sendcounts[rank], MPI_DOUBLE,
        result.data(), sendcounts.data(), displs.data(), MPI_DOUBLE,
        0, MPI_COMM_WORLD);

    return result;
}