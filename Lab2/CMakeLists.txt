cmake_minimum_required(VERSION 4.3)

set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD 451f2fe2-a8a2-47c3-bc32-94786d8fc91b)

project(Lab2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_CXX_MODULE_STD ON)

find_package(OpenMP REQUIRED)

add_executable(Lab2 main.cpp)

target_sources(Lab2
    PRIVATE FILE_SET cxx_modules TYPE CXX_MODULES FILES
        matrix.cppm
        matrix_io.cppm
        matrix_multiply.cppm
)

if(OpenMP_CXX_FOUND)
    target_link_libraries(Lab2 PRIVATE OpenMP::OpenMP_CXX)

    target_include_directories(Lab2 PRIVATE ${OpenMP_CXX_INCLUDE_DIRS})
endif()

if(MSVC)
    target_compile_options(Lab2
        PRIVATE
        /W4
        /EHsc
    )
else()
    target_compile_options(Lab2
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