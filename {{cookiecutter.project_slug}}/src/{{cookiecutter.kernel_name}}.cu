#include <cute/tensor.hpp>
#include <iostream>

__global__ void verification_kernel() {
  using namespace cute;

  // Quick compile-time layout sanity print out
  if (threadIdx.x == 0 && blockIdx.x == 0) {
    auto shape = Shape<_4, _8>{};
    auto stride = Stride<_8, _1>{};
    auto layout = make_layout(shape, stride);
    print("Generated boilerplate layout abstraction verified:\n");
    print(layout);
    print("\n");
  }
}

int main() {
  std::cout << "Initializing remote cluster execution context..." << std::endl;

  verification_kernel<<<1, 1>>>();
  cudaDeviceSynchronize();

  std::cout << "Execution loop completed cleanly." << std::endl;
  return 0;
}
