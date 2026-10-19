cmake_minimum_required(VERSION 3.20)

project(Lab3 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(WIN32)
    set(MPI_CXX_HEADER_DIR "C:/Program Files (x86)/Microsoft SDKs/MPI/Include" CACHE PATH "MS-MPI Include")
    set(MPI_CXX_LIB_NAMES "msmpi" CACHE STRING "MS-MPI Lib Name")
    set(MPI_msmpi_LIBRARY "C:/Program Files (x86)/Microsoft SDKs/MPI/Lib/x64/msmpi.lib" CACHE FILEPATH "MS-MPI Library")
endif()

find_package(MPI REQUIRED)

add_executable(Lab3
    main.cpp
    matrix_io.cpp
    matrix_multiply.cpp
    mpi_utils.cpp
)

target_link_libraries(Lab3 PRIVATE MPI::MPI_CXX)

if(MSVC)
    target_compile_options(Lab3 PRIVATE /W4 /EHsc)
else()
    target_compile_options(Lab3 PRIVATE -Wall -Wextra -Wpedantic -O2)
endif()

configure_file(matrix_a.txt ${CMAKE_CURRENT_BINARY_DIR}/matrix_a.txt COPYONLY)
configure_file(matrix_b.txt ${CMAKE_CURRENT_BINARY_DIR}/matrix_b.txt COPYONLY)