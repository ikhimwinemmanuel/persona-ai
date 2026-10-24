
import shutil
import subprocess
import zipfile
from pathlib import Path

# Locate the backend directory
BASE_DIR = Path(__file__).resolve().parent

# Define build paths
BUILD_DIR = BASE_DIR / ".lambda-build"
ZIP_PATH = BASE_DIR / ".lambda-build" / "personaai-lambda.zip"

# Files required by our Lambda application
APP_FILES = [
    "server.py",
    "lambda_handler.py",
    "context.py",
    "resources.py",
]


def build():
    # 1. Start with a clean build directory
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    BUILD_DIR.mkdir()

    package_dir = BUILD_DIR / "package"
    package_dir.mkdir()

    # 2. Export production dependencies
    subprocess.run(
        [
            "uv", "export",
            "--format", "requirements-txt",
            "--no-dev",
            "--no-hashes",
            "--no-emit-project",
            "-o", "requirements-lambda.txt",
        ],
        cwd=BASE_DIR,
        check=True,
    )

    # 3. Install dependencies inside Linux Docker
    subprocess.run(
        [
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "-v", f"{BASE_DIR}:/workspace",
            "-w", "/workspace",
            "python:3.12-slim",
            "sh", "-c",
            "python -m pip install --no-cache-dir "
            "-r requirements-lambda.txt "
            "-t .lambda-build/package",
        ],
        check=True,
    )

    # 4. Copy application source files
    for filename in APP_FILES:
        shutil.copy2(BASE_DIR / filename, package_dir / filename)

    # 5. Copy professional knowledge files
    shutil.copytree(BASE_DIR / "data", package_dir / "data")

    # 6. Create Lambda ZIP package
    with zipfile.ZipFile(
        ZIP_PATH, "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for file in package_dir.rglob("*"):
            if file.is_file():
                archive.write(
                    file,
                    file.relative_to(package_dir)
                )

    print(f"Lambda package created: {ZIP_PATH}")


if __name__ == "__main__":
    build()
