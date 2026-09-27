cmake_minimum_required(VERSION 4.3)

set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD 451f2fe2-a8a2-47c3-bc32-94786d8fc91b)

project(ParallelLab1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_CXX_MODULE_STD ON)

add_executable(ParallelLab1 main.cpp)

target_sources(ParallelLab1
    PRIVATE FILE_SET cxx_modules TYPE CXX_MODULES FILES
        matrix.cppm
        matrix_io.cppm
        matrix_multiply.cppm
)

if(MSVC)
    target_compile_options(ParallelLab1
        PRIVATE
        /W4
        /EHsc
    )

else()
    target_compile_options(ParallelLab1
        PRIVATE
        -Wall
        -Wextra
        -Wpedantic
    )

endif()

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/matrix_a.txt
    ${CMAKE_CURRENT_BINARY_DIR}/matrix_a.txt
    COPYONLY
)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/matrix_b.txt
    ${CMAKE_CURRENT_BINARY_DIR}/matrix_b.txt
    COPYONLY
)