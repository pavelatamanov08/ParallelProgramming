export module matrix_multiply;

import std;
import matrix;

export Matrix multiplySequential(const Matrix& a, const Matrix& b)
{
    if (a.size() != b.size())
    {
        throw std::invalid_argument("Matrix sizes must be equal.");
    }

    const std::size_t n = a.size();

    Matrix result(n);

    for (std::size_t i = 0; i < n; ++i)
    {
        for (std::size_t k = 0; k < n; ++k)
        {
            const double value = a(i, k);

            for (std::size_t j = 0; j < n; ++j)
            {
                result(i, j) += value * b(k, j);
            }
        }
    }
    return result;
}


export Matrix multiplyParallel(const Matrix& a, const Matrix& b, std::size_t threadCount)
{
    if (a.size() != b.size())
    {
        throw std::invalid_argument( "Matrix sizes must be equal.");
    }

    const std::size_t n = a.size();

    if (threadCount == 0)
    {
        threadCount = 1;
    }

    threadCount = std::min(threadCount, n);

    Matrix result(n);

    std::vector<std::thread> workers;

    workers.reserve(threadCount);

    const std::size_t baseRows = n / threadCount;

    const std::size_t extraRows = n % threadCount;

    std::size_t begin = 0;

    for (std::size_t t = 0; t < threadCount; ++t)
    {
        const std::size_t rows = baseRows + (t < extraRows ? 1 : 0);

        const std::size_t end = begin + rows;

        workers.emplace_back([&, begin, end]()
            {
                for (std::size_t i = begin; i < end; ++i)
                {
                    for (std::size_t k = 0; k < n; ++k)
                    {
                        const double value = a(i, k);
                        for (std::size_t j = 0; j < n; ++j)
                        {
                            result(i, j) += value * b(k, j);
                        }
                    }
                }
            }
        );

        begin = end;
    }

    for (auto& worker : workers)
    {
        worker.join();
    }

    return result;
}