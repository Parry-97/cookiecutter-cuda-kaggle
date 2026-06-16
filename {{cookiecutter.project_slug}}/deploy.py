# deploy.py
import os
import base64
import subprocess


def get_self_contained_script(cmake_b64, cuda_b64, binary_name, cu_filename):
    return f"""import os
import base64
import subprocess
import sys

CMAKE_B64 = "{cmake_b64}"
CUDA_B64 = "{cuda_b64}"

def execute(cmd):
    print(f"--> Running: {{cmd}}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        print(f"ERROR: Command failed with exit code {{process.returncode}}")
        sys.exit(process.returncode)

# 1. Rehydrate the project files on the remote Kaggle VM
os.makedirs("src", exist_ok=True)
with open("CMakeLists.txt", "wb") as f:
    f.write(base64.b64decode(CMAKE_B64))
with open(f"src/{cu_filename}", "wb") as f:
    f.write(base64.b64decode(CUDA_B64))

# 2. Fetch the CUTLASS framework dependency
if not os.path.exists("cutlass"):
    execute("git clone --recursive https://github.com/NVIDIA/cutlass.git")

# 3. Trigger native remote compilation
execute("cmake -B build -S . -DBUILD_TARGET=KAGGLE")
execute("cmake --build build --parallel $(nproc)")

# 4. Run the final compiled execution binary
print("\\n=== STARTING HARDWARE BENCHMARK ===")
execute("./build/{binary_name}")
print("=== BENCHMARK COMPLETE ===")
"""


def main():
    # 1. Read and base64-encode local build files
    if not os.path.exists("CMakeLists.txt"):
        print("Error: CMakeLists.txt not found in current directory.")
        return

    with open("CMakeLists.txt", "rb") as f:
        cmake_b64 = base64.b64encode(f.read()).decode("utf-8")

    src_files = [f for f in os.listdir("src") if f.endswith(".cu")]
    if not src_files:
        print("Error: No .cu files found in src/ directory.")
        return
    cu_filename = "{{cookiecutter.kernel_name}}.cu"
    binary_name = "{{cookiecutter.kernel_name}}"

    with open(f"src/{cu_filename}", "rb") as f:
        cuda_b64 = base64.b64encode(f.read()).decode("utf-8")

    # 2. Generate the dynamic run_job.py
    print("Packing project assets into a self-contained runtime payload...")
    payload = get_self_contained_script(cmake_b64, cuda_b64, binary_name, cu_filename)
    with open("run_job.py", "w") as f:
        f.write(payload)

    # 3. Fire off the execution command via the Kaggle CLI
    print("Pushing self-contained bundle to Kaggle cluster...")
    subprocess.run("kaggle kernels push -p .", shell=True)


if __name__ == "__main__":
    main()
