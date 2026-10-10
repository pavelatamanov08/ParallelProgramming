export module matrix_io;

import std;
import matrix;

export Matrix readMatrix(const std::string& filename)
{
    std::ifstream input(filename);

    if (!input)
    {
        throw std::runtime_error( "Cannot open file: " + filename);
    }

    std::size_t n = 0;

    input >> n;

    if (!input || n == 0)
    {
        throw std::runtime_error( "Invalid matrix size in file: " + filename);
    }

    Matrix matrix(n);

    for (std::size_t i = 0; i < n; ++i)
    {
        for (std::size_t j = 0; j < n; ++j)
        {
            if (!(input >> matrix(i, j)))
            {
                throw std::runtime_error( "Not enough matrix values in file: " + filename);
            }
        }
    }
    return matrix;
}

export void writeMatrix(const Matrix& matrix, const std::string& filename)
{
    std::ofstream output(filename);

    if (!output)
    {
        throw std::runtime_error( "Cannot create file: " + filename
        );
    }

    output << matrix.size() << '\n';
    output << std::setprecision(17);

    for (std::size_t i = 0; i < matrix.size(); ++i)
    {
        for (std::size_t j = 0; j < matrix.size(); ++j)
        {
            if (j != 0)
            {
                output << ' ';
            }
            output << matrix(i, j);
        }
        output << '\n';
    }
}

export void appendBenchmark(const std::string& filename, std::size_t matrixSize, std::size_t threadCount, double sequentialMs, double parallelMs)
{
    const bool exists = std::filesystem::exists(filename);

    std::ofstream output( filename, std::ios::app);

    if (!output)
    {
        throw std::runtime_error( "Cannot create benchmark file.");
    }

    if (!exists)
    {
        output << "matrix_size," << "threads," << "sequential_ms," << "parallel_ms," << "speedup\n";
    }

    const double speedup = parallelMs > 0.0 ? sequentialMs / parallelMs : 0.0;

    output << matrixSize << ',' << threadCount << ',' << std::setprecision(10) << sequentialMs << ',' << parallelMs << ',' << speedup << '\n';
}