# cookiecutter-cuda-kaggle

A high-performance **CUDA C++ and NVIDIA CUTLASS 3.x (CuTe)** development template tailored for terminal-centric environments (Neovim v0.12 / Clangd). 

This template implements a specialized **Asymmetric Cross-Compilation Workflow**: you author, navigate, and compile-check your code locally (catching syntax and template errors instantly on your CPU), then offload the actual hardware execution and Nsight profiling to a remote Kaggle cloud instance equipped with an NVIDIA Tesla T4 GPU.

---

## 🚀 Key Features

* **Zero-Overhead Cloud Offloading:** Bypasses Kaggle's single-file CLI upload limitations using a customized Base64 serialization packer (`deploy.py`).
* **Flawless Neovim v0.12 Integration:** Pre-configured `.clangd` and `compile_flags.txt` mappings resolve deep, template-heavy CUTLASS 3.x and CuTe layouts with zero editor diagnostic lag.
* **Smart Dual-Target CMake Configuration:** Compile-checks code locally targeting Turing Tensor Core specifications (`sm_75`) to catch layout mismatches before pushing to the cloud.
* **Headless Infrastructure Automation:** Clones framework dependencies, builds the target natively using the cloud VM's local toolchain (preventing `GLIBC` dynamic runtime errors)

---

## 📂 Project Structure

When you generate a project from this template, it instantiates the following architecture:

```text
├── .clangd                 # Custom Clangd rules targeting sm_75 and Arch/EndeavourOS paths
├── compile_flags.txt       # 0-byte anchor file forcing Clangd to resolve relative paths from root
├── CMakeLists.txt          # Smart dual-environment build orchestration layout
├── kernel-metadata.json    # Deployment specifications for the Kaggle API
├── deploy.py               # Local asset packaging and remote triggering automation script
└── src/
    └── gemm_kernel.cu      # Master CUDA C++ source file with robust error macro and reset hooks

```

---

## 🛠️ Prerequisites

### Local Development Machine (e.g., Arch Linux / EndeavourOS)

Ensure your terminal environment has the core toolchains installed:

```bash
sudo pacman -S cuda cmake cookiecutter python-pip

```

Ensure your Kaggle API credentials token is correctly placed at `~/.kaggle/kaggle.json` and secured (`chmod 600`).

### Remote Dependencies

The deployment script handles the automated configuration of NVIDIA's **CUTLASS 3.x** framework directly on the remote instance.

---

## ⚙️ Quick Start

### 1. Instantiate the Template

Run cookiecutter pointing to your template directory (or repository path):

```bash
cookiecutter /path/to/cookiecutter-cuda-kaggle

```

Fill out the interactive prompt values (e.g., `project_name`, `kernel_name`).

### 2. Enter the Workspace & Fetch Header Files

Navigate into your newly generated directory and clone a local copy of the CUTLASS framework. **Note:** Because CUTLASS is a header-only library, we only keep it locally to feed autocomplete, type validation, and syntax checking to our text editor.

```bash
cd <your_project_slug>
mkdir extern
git clone --recursive [https://github.com/NVIDIA/cutlass.git](https://github.com/NVIDIA/cutlass.git) extern/cutlass

```

### 3. Initialize Neovim v0.12 Buffer Context

Open the master source file. `clangd` will catch the `compile_flags.txt` anchor, parse the root `.clangd` paths, and provide instant diagnostics without any configuration modifications:

```bash
xdg-open src/<kernel_name>.cu

```

---

## 🔄 The Hybrid Development Loop

This project setup splits compute tasks logically to maximize development speeds:

### Step 1: Write & Compile-Check Code Locally

Modify your layout logic or matrix transformations in `src/`. To check for syntax flaws, template configuration problems, or invalid coordinate assignments, compile your workspace locally:

```bash
# Configure the local build directory to mimic remote targets
cmake -B build -S . -DBUILD_TARGET=KAGGLE

# Run the local compiler pass
cmake --build build

```

* **Why this works:** The local CPU and compiler process all your code definitions targeting `sm_75`. If there is a missing semicolon or type mismatch, it fails immediately on your laptop.
* **Note:** If it compiles successfully, do not execute the binary inside `./build` locally; your local GPU might not be able to execute instructions compiled for Turing Tensor Cores.

### Step 2: Push & Execute headlessly on the Cloud Accelerator

Once your code compiles locally with zero errors, execute the deployment script from your terminal:

```bash
python deploy.py

```

#### Behind the Scenes:

1. `deploy.py` reads `CMakeLists.txt` and `src/<kernel_name>.cu`, converts them into safe Base64 strings, and embeds them into a dynamic runtime payload (`run_job.py`).
2. It pushes only the lightweight orchestrator to Kaggle, leaving your heavy local `extern/cutlass` folder untouched.
3. The Kaggle cloud VM boots up, extracts your project files, pulls down a fresh framework clone natively, and compiles the source code against its own operating system library version.
4. The script executes the final kernel
---

## ⚠️ Troubleshooting & System Notes

* **Silent Kernel Drops:** CUDA launches are asynchronous and fail silently by default. Always wrap host-side synchronization operations inside the pre-configured `CUDA_CHECK()` validation macro provided in the file to intercept hardware allocation or thread configuration limits instantly.
* **Platform Artifact Warnings:** You will see minor `nbconvert` or `SyntaxWarning` notifications from packages like `mistune` at the conclusion of your cloud logs. These are completely harmless background actions executed by the Kaggle presentation platform when it converts your runtime script to a graphical web log (`__results__.html`) and have zero impact on your core execution statistics.
