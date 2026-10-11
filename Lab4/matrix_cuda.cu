#include "matrix_cuda.cuh"

#include <cuda_runtime.h>
#include <iostream>
#include <stdexcept>

template <int TILE>
__global__ void matMulTiled(const double* A, const double* B,
                            double* C, int n) {
    __shared__ double tileA[TILE][TILE];
    __shared__ double tileB[TILE][TILE];

    int row = blockIdx.y * TILE + threadIdx.y;
    int col = blockIdx.x * TILE + threadIdx.x;

    double sum = 0.0;

    const int numTiles = (n + TILE - 1) / TILE;

    for (int t = 0; t < numTiles; ++t) {
        int aCol = t * TILE + threadIdx.x;
        if (row < n && aCol < n) {
            tileA[threadIdx.y][threadIdx.x] = A[row * n + aCol];
        } else {
            tileA[threadIdx.y][threadIdx.x] = 0.0;
        }

        int bRow = t * TILE + threadIdx.y;
        if (bRow < n && col < n) {
            tileB[threadIdx.y][threadIdx.x] = B[bRow * n + col];
        } else {
            tileB[threadIdx.y][threadIdx.x] = 0.0;
        }

        __syncthreads();

        #pragma unroll
        for (int k = 0; k < TILE; ++k) {
            sum += tileA[threadIdx.y][k] * tileB[k][threadIdx.x];
        }

        __syncthreads();
    }

    if (row < n && col < n) {
        C[row * n + col] = sum;
    }
}

double multiplyCuda(const Matrix& a, const Matrix& b,
                    Matrix& result,
                    int blockSize) {
    if (a.size() != b.size()) {
        throw std::invalid_argument("Matrix dimensions must match.");
    }
    if (blockSize != 8 && blockSize != 16 && blockSize != 32) {
        throw std::invalid_argument("blockSize must be 8, 16 or 32.");
    }

    const int n = static_cast<int>(a.size());
    const std::size_t bytes = static_cast<std::size_t>(n) * n * sizeof(double);

    double* d_A = nullptr;
    double* d_B = nullptr;
    double* d_C = nullptr;

    cudaError_t err = cudaMalloc(&d_A, bytes);
    if (err != cudaSuccess) throw std::runtime_error("cudaMalloc failed for A");
    err = cudaMalloc(&d_B, bytes);
    if (err != cudaSuccess) throw std::runtime_error("cudaMalloc failed for B");
    err = cudaMalloc(&d_C, bytes);
    if (err != cudaSuccess) throw std::runtime_error("cudaMalloc failed for C");

    cudaMemcpy(d_A, a.data(), bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, b.data(), bytes, cudaMemcpyHostToDevice);

    dim3 threads(blockSize, blockSize);
    dim3 grid((n + blockSize - 1) / blockSize,
              (n + blockSize - 1) / blockSize);

    auto launch = [&]() {
        switch (blockSize) {
            case  8: matMulTiled< 8><<<grid, threads>>>(d_A, d_B, d_C, n); break;
            case 16: matMulTiled<16><<<grid, threads>>>(d_A, d_B, d_C, n); break;
            case 32: matMulTiled<32><<<grid, threads>>>(d_A, d_B, d_C, n); break;
        }
    };

    launch();
    cudaDeviceSynchronize();

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    launch();
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms = 0.0f;
    cudaEventElapsedTime(&ms, start, stop);

    cudaMemcpy(result.data(), d_C, bytes, cudaMemcpyDeviceToHost);

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);

    return static_cast<double>(ms);
}