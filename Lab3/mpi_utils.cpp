#include <mpi.h>
#include "mpi_utils.hpp"

MPIEnvironment::MPIEnvironment(int& argc, char**& argv) {
    int provided;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);
}

MPIEnvironment::~MPIEnvironment() {
    MPI_Finalize();
}

int getRank() {
    int r; MPI_Comm_rank(MPI_COMM_WORLD, &r); return r;
}

int getSize() {
    int s; MPI_Comm_size(MPI_COMM_WORLD, &s); return s;
}