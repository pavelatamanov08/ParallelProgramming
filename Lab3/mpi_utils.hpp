#pragma once

class MPIEnvironment {
public:
    MPIEnvironment(int& argc, char**& argv);
    ~MPIEnvironment();

    MPIEnvironment(const MPIEnvironment&) = delete;
    MPIEnvironment& operator=(const MPIEnvironment&) = delete;
};

int getRank();
int getSize();