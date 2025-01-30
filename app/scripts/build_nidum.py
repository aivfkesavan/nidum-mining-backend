import site
import subprocess
import sys
import os 
import pkgutil

def run():
    site_packages = site.getsitepackages()[0]
    command = [
        f"{sys.executable}", "-m", "nuitka", "nidum/main.py",
        "--company-name=nidumai",
        "--product-name=nidum",
        "--output-dir=dist",
        "--follow-imports",
        "--standalone",
        "--output-filename=nidum",
        "--python-flag=no_site",
        "--onefile"
    ]

    if sys.platform == "darwin": 
        command.extend([
            "--macos-app-name=nidum",
            "--macos-app-mode=gui",
            "--macos-app-version=0.0.1",
            "--macos-signed-app-name=com.nidum.mining",
            "--include-distribution-meta=mlx",
            "--include-module=mlx._reprlib_fix",
            "--include-module=mlx._os_warning",
            f"--include-data-files={site_packages}/mlx/lib/mlx.metallib=mlx/lib/mlx.metallib",
            f"--include-data-files={site_packages}/mlx/lib/mlx.metallib=./mlx.metallib",
            "--include-distribution-meta=pygments",
            "--nofollow-import-to=tinygrad"
        ])
        inference_modules = [
            name for _, name, _ in pkgutil.iter_modules(['nidum/inference/mlx/models'])
        ]
        for module in inference_modules:
            command.append(f"--include-module=nidum.inference.mlx.models.{module}")
    elif sys.platform == "win32":  
        command.extend([
            "--windows-icon-from-ico=docs/nidum-logo-win.ico",
            "--file-version=0.0.1",
            "--product-version=0.0.1"
        ])
    elif sys.platform.startswith("linux"):  
        command.extend([
            "--include-distribution-metadata=pygments",
            "--linux-icon=docs/nidum-rounded.png"
        ])

    try:
        subprocess.run(command, check=True)
        print("Build completed!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run()
