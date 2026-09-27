import std;

import matrix;
import matrix_io;
import matrix_multiply;

namespace
{
    bool matricesEqual(const Matrix& a, const Matrix& b, double epsilon = 1e-9)
    {
        if (a.size() != b.size())
        {
            return false;
        }

        for (std::size_t i = 0; i < a.size(); ++i)
        {
            for (std::size_t j = 0; j < a.size(); ++j)
            {
                if (std::abs(a(i, j) - b(i, j)) > epsilon)
                {
                    return false;
                }
            }
        }

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

int main()
{
    try
    {
        const Matrix a = readMatrix("matrix_a.txt");

        const Matrix b = readMatrix("matrix_b.txt");

        if (a.size() != b.size())
        {
            throw std::runtime_error("The matrices must have the same dimensions.");
        }

        const std::size_t n = a.size();

        std::size_t threadCount = std::thread::hardware_concurrency();

        if (threadCount == 0)
        {
            threadCount = 4;
        }

        threadCount = std::min(threadCount, n);

        std::cout << "Parallel Programming - Laboratory Work 1\n";

        std::cout << "Matrix multiplication\n\n";

        std::cout << "Matrix size: " << n << " x " << n << '\n';

        std::cout << "Threads: " << threadCount << "\n\n";

        const auto [sequentialResult, sequentialMs] = measure([&](){ return multiplySequential(a, b); });

        const auto [parallelResult, parallelMs] = measure([&](){ return multiplyParallel(a, b, threadCount); });

        const bool correct = matricesEqual( sequentialResult, parallelResult);

        writeMatrix(parallelResult, "result.txt");

        appendBenchmark("benchmark.csv", n, threadCount, sequentialMs, parallelMs);

        const double speedup = parallelMs > 0.0 ? sequentialMs / parallelMs : 0.0;

        std::cout << "Sequential time: " << sequentialMs << " ms\n";

        std::cout << "Parallel time:   " << parallelMs << " ms\n";

        std::cout << "Speedup:         " << speedup << '\n';

        std::cout << "Result check: " << (correct ? "OK" : "FAILED") << '\n';

        std::cout << "\nResult: result.txt\n";

        std::cout << "Benchmark: benchmark.csv\n";

        return correct ? 0 : 2;
    }
    catch (const std::exception& error)
    {
        std::cerr << "ERROR: " << error.what() << '\n';

        return 1;
    }
}