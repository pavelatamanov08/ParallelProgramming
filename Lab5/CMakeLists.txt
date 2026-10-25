cmake_minimum_required(VERSION 3.15)

# Явно указываем, что проект использует и C, и C++
project(MandelbrotLab C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(Threads REQUIRED)

# 1. Создаем библиотеку getopt
add_library(my_getopt STATIC getopt.c)

# 2. ПРИНУДИТЕЛЬНО указываем язык линковки C для этой библиотеки
set_target_properties(my_getopt PROPERTIES LINKER_LANGUAGE C)

target_include_directories(my_getopt PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# 3. Основная программа
add_executable(mandelbrot
    main.cpp
    mandelbrotSerial.cpp
    mandelbrotThread.cpp
    ../common/ppm.cpp
)

target_include_directories(mandelbrot PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../common
)

target_link_libraries(mandelbrot PRIVATE Threads::Threads my_getopt)

if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    target_compile_options(mandelbrot PRIVATE $<$<CONFIG:Release>:/O2>)
else()
    target_compile_options(mandelbrot PRIVATE -O3)
endif()