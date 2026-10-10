import std;

import matrix;
import matrix_io;
import matrix_multiply;

namespace
{
    bool matricesEqual(const Matrix& a, const Matrix& b, double epsilon = 1e-9)
    {
        if (a.size() != b.size()) return false;
        for (std::size_t i = 0; i < a.size(); ++i)
            for (std::size_t j = 0; j < a.size(); ++j)
                if (std::abs(a(i, j) - b(i, j)) > epsilon) return false;
        return true;
    }

    template <class Function>
    std::pair<Matrix, double> measure(Function&& function)
    {
        const auto start = std::chrono::steady_clock::now();
        Matrix result = function();
        const auto finish = std::chrono::steady_clock::now();
        const double milliseconds = std::chrono::duration<double, std::milli>(finish - start).count();
        return { std::move(result), milliseconds };
    }
}

int main(int argc, char* argv[])
{
    try
    {
        std::size_t n = 500;
        int threadCount = 4;

        if (argc >= 2) {
            n = std::stoul(argv[1]);
        }
        if (argc >= 3) {
            threadCount = std::stoi(argv[2]);
        }

        Matrix a, b;

        if (n == 500) {
            a = readMatrix("matrix_a.txt");
            b = readMatrix("matrix_b.txt");
        }
        else {
            std::cout << "Generating random matrices in memory for size " << n << "...\n";
            a = Matrix(n);
            b = Matrix(n);
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(0.0, 9.0);
            for (std::size_t i = 0; i < n; ++i)
                for (std::size_t j = 0; j < n; ++j) {
                    a(i, j) = dis(gen);
                    b(i, j) = dis(gen);
                }
        }

        if (a.size() != b.size())
        {
            throw std::runtime_error("The matrices must have the same dimensions.");
        }

        std::cout << "Parallel Programming - Laboratory Work 2 (OpenMP)\n";
        std::cout << "Matrix size: " << n << " x " << n << '\n';
        std::cout << "Threads: " << threadCount << "\n\n";

        const auto [sequentialResult, sequentialMs] = measure([&]() { return multiplySequential(a, b); });

        const auto [parallelResult, parallelMs] = measure([&]() { return multiplyParallel(a, b, threadCount); });

        const bool correct = matricesEqual(sequentialResult, parallelResult);

        writeMatrix(parallelResult, "result.txt");
        appendBenchmark("benchmark.csv", n, threadCount, sequentialMs, parallelMs);

        const double speedup = parallelMs > 0.0 ? sequentialMs / parallelMs : 0.0;

        std::cout << "Sequential time: " << sequentialMs << " ms\n";
        std::cout << "Parallel time:   " << parallelMs << " ms\n";
        std::cout << "Speedup:         " << speedup << '\n';
        std::cout << "Result check: " << (correct ? "OK" : "FAILED") << '\n';

        return correct ? 0 : 2;
    }
    catch (const std::exception& error)
    {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}