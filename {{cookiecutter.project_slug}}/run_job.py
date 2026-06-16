import os
import subprocess
import sys


def execute(cmd):
    print(f"--> Running: {cmd}")
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        print(f"ERROR: Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)


# 1. Direct environment dependency validation
if not os.path.exists("cutlass"):
    execute("git clone --recursive https://github.com/NVIDIA/cutlass.git")

# 2. Build via local cloud context (prevents GLIBC dynamic runtime traps)
execute("cmake -B build -S . -DBUILD_TARGET=KAGGLE")
execute("cmake --build build --parallel $(nproc)")

# 3. Clean environment boundary hardware verification
print("\n=== STARTING HARDWARE BENCHMARK ===")
execute("./build/{{cookiecutter.kernel_name}}")
print("=== BENCHMARK COMPLETE ===")
