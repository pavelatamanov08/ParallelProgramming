#include <mpi.h>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <utility>
#include <stdexcept>
#include <cmath>

#include "matrix.hpp"
#include "matrix_io.hpp"
#include "matrix_multiply.hpp"
#include "mpi_utils.hpp"

namespace {
    bool matricesEqual(const Matrix& a, const Matrix& b, double eps = 1e-9) {
        if (a.size() != b.size()) return false;
        for (std::size_t i = 0; i < a.size(); ++i)
            for (std::size_t j = 0; j < a.size(); ++j)
                if (std::fabs(a(i, j) - b(i, j)) > eps) return false;
        return true;
    }

    std::pair<Matrix, double> measure_seq(const Matrix& a, const Matrix& b) {
        auto s = std::chrono::steady_clock::now();
        Matrix r = multiplySequential(a, b);
        auto e = std::chrono::steady_clock::now();
        return std::make_pair(std::move(r), std::chrono::duration<double, std::milli>(e - s).count());
    }

    std::pair<Matrix, double> measure_mpi(const Matrix& a, const Matrix& b) {
        auto s = std::chrono::steady_clock::now();
        Matrix r = multiplyMPI(a, b);
        auto e = std::chrono::steady_clock::now();
        return std::make_pair(std::move(r), std::chrono::duration<double, std::milli>(e - s).count());
    }
}

int main(int argc, char** argv) {
    MPIEnvironment env(argc, argv);
    const int rank = getRank();
    const int size = getSize();

    try {
        std::size_t n = 0;
        Matrix a, b;

        if (rank == 0) {
            a = readMatrix("matrix_a.txt");
            b = readMatrix("matrix_b.txt");
            if (a.size() != b.size())
                throw std::runtime_error("Matrix sizes differ.");
            n = a.size();

            std::cout << "Laboratory Work 3: Sequential + MPI\n";
            std::cout << "Matrix size: " << n << " x " << n << "\n";
            std::cout << "MPI processes: " << size << "\n\n";
        }

        MPI_Bcast(&n, 1, MPI_UNSIGNED_LONG_LONG, 0, MPI_COMM_WORLD);
        if (rank != 0) { a = Matrix(n); b = Matrix(n); }

        double seqMs = 0.0;
        Matrix seqRes(n);
        if (rank == 0) {
            std::pair<Matrix, double> result = measure_seq(a, b);
            seqRes = std::move(result.first);
            seqMs = result.second;
        }

        double mpiMs = 0.0;
        Matrix mpiRes(n);
        if (rank == 0) {
            std::pair<Matrix, double> result = measure_mpi(a, b);
            mpiRes = std::move(result.first);
            mpiMs = result.second;
        }
        else {
            multiplyMPI(a, b);
        }

        if (rank == 0) {
            const bool okMpi = matricesEqual(seqRes, mpiRes);

            writeMatrix(mpiRes, "result.txt");
            appendBenchmark("benchmark.csv", n, seqMs, mpiMs, size);

            std::cout << std::fixed << std::setprecision(3);
            std::cout << "Sequential:   " << seqMs << " ms\n";
            std::cout << "MPI (" << size << " procs):  " << mpiMs << " ms  "
                << "(speedup " << (mpiMs > 0 ? seqMs / mpiMs : 0) << ")\n\n";
            std::cout << "MPI vs Sequential: " << (okMpi ? "OK" : "FAILED") << "\n";

            return okMpi ? 0 : 2;
        }
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "Rank " << rank << ": " << e.what() << "\n";
        MPI_Abort(MPI_COMM_WORLD, 1);
        return 1;
    }
}