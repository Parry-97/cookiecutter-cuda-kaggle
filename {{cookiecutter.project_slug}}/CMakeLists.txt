cmake_minimum_required(VERSION 3.18)
project({{cookiecutter.project_slug}} LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

set(BUILD_TARGET "KAGGLE" CACHE STRING "Target hardware environment: KAGGLE or LOCAL")

if(BUILD_TARGET STREQUAL "LOCAL")
    set(CMAKE_CUDA_ARCHITECTURES {{cookiecutter.local_compute_capability}})
    message(STATUS "Configuring for Local Execution (sm_{{cookiecutter.local_compute_capability}})")
else()
    set(CMAKE_CUDA_ARCHITECTURES {{cookiecutter.remote_compute_capability}})
    message(STATUS "Configuring for Remote Cross-Compilation (sm_{{cookiecutter.remote_compute_capability}})")
endif()

if(DEFINED ENV{KAGGLE_CONTAINER_NAME})
    include_directories(/kaggle/working/cutlass/include)
else()
    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/extern/cutlass/include)
endif()

add_executable({{cookiecutter.kernel_name}} src/{{cookiecutter.kernel_name}}.cu)
set_target_properties({{cookiecutter.kernel_name}} PROPERTIES CUDA_SEPARABLE_COMPILATION OFF)
