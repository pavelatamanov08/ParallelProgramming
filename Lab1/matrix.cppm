export module matrix;

import std;

export class Matrix
{
public:
    Matrix() = default;

    explicit Matrix(std::size_t size) : _size(size), _data(size* size, 0.0)
    {
        if (size == 0)
        {
            throw std::invalid_argument("Matrix size must be greater than zero.");
        }
    }

    [[nodiscard]]
    std::size_t size() const noexcept
    {
        return _size;
    }

    double& operator()(std::size_t row, std::size_t column)
    {
        return _data[row * _size + column];
    }

    const double& operator()(std::size_t row, std::size_t column) const
    {
        return _data[row * _size + column];
    }

private:
    std::size_t _size = 0;
    std::vector<double> _data;
};