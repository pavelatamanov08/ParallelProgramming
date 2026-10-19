#include "matrix_io.hpp"

#include <fstream>
#include <iomanip>
#include <stdexcept>

Matrix readMatrix(const std::string& filename) {
    std::ifstream input(filename);
    if (!input) {
        throw std::runtime_error("Cannot open file: " + filename);
    }

    std::size_t n = 0;
    input >> n;
    if (!input || n == 0) {
        throw std::runtime_error("Invalid matrix size in file: " + filename);
    }

    Matrix matrix(n);
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            if (!(input >> matrix(i, j))) {
                throw std::runtime_error("Not enough matrix values in file: " + filename);
            }
        }
    }
    return matrix;
}

void writeMatrix(const Matrix& matrix, const std::string& filename) {
    std::ofstream output(filename);
    if (!output) {
        throw std::runtime_error("Cannot create file: " + filename);
    }

    output << matrix.size() << '\n';
    output << std::setprecision(17);

    for (std::size_t i = 0; i < matrix.size(); ++i) {
        for (std::size_t j = 0; j < matrix.size(); ++j) {
            if (j != 0) output << ' ';
            output << matrix(i, j);
        }
        output << '\n';
    }
}

void appendBenchmark(const std::string& filename,
    std::size_t matrixSize,
    double sequentialMs,
    double mpiMs,
    std::size_t mpiProcs) {
    bool exists = false;
    {
        std::ifstream check(filename);
        exists = check.good();
    }

    std::ofstream out(filename, std::ios::app);
    if (!out) throw std::runtime_error("Cannot create benchmark file.");

    if (!exists) {
        out << "matrix_size,sequential_ms,mpi_ms,mpi_speedup,mpi_procs\n";
    }

    const double mpiSpeedup = mpiMs > 0 ? sequentialMs / mpiMs : 0.0;

    out << matrixSize << ','
        << std::setprecision(10) << sequentialMs << ','
        << mpiMs << ','
        << mpiSpeedup << ','
        << mpiProcs << '\n';
}