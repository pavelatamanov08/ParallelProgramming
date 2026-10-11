cmake_minimum_required(VERSION 3.20)

if(WIN32)
    set(CMAKE_CUDA_COMPILER
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.4/bin/nvcc.exe")
endif()

project(Lab4 LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

set(CMAKE_CUDA_ARCHITECTURES native)
#set(CMAKE_CUDA_ARCHITECTURES 75 80 86)

add_executable(Lab4
    main.cu
    matrix_io.cpp
    matrix_cpu.cpp
    matrix_cuda.cu
)

set_source_files_properties(matrix_io.cpp matrix_cpu.cpp
    PROPERTIES LANGUAGE CXX)

set_source_files_properties(main.cu matrix_cuda.cu
    PROPERTIES LANGUAGE CUDA)

target_include_directories(Lab4 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

if(MSVC)
    target_compile_options(Lab4 PRIVATE $<$<COMPILE_LANGUAGE:CXX>:/W4 /EHsc>)
else()
    target_compile_options(Lab4 PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-Wall -Wextra -Wpedantic>)
endif()