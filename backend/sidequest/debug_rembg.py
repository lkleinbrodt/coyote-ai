"""
Debug script to test rembg installation and import
"""

import sys
import subprocess


def check_pip_packages():
    """Check what packages are installed"""
    print("=== Checking installed packages ===")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"], capture_output=True, text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error checking packages: {e}")


def check_rembg_import():
    """Test rembg import"""
    print("\n=== Testing rembg import ===")

    # Method 1: Direct import
    try:
        import rembg

        print("✓ Direct import successful")
        print(f"  rembg version: {rembg.__version__}")
        print(f"  rembg location: {rembg.__file__}")
        return True
    except ImportError as e:
        print(f"✗ Direct import failed: {e}")

    # Method 2: Try importing specific function
    try:
        from rembg import remove

        print("✓ Function import successful")
        return True
    except ImportError as e:
        print(f"✗ Function import failed: {e}")

    # Method 3: Check if it's in site-packages
    try:
        import site

        for path in site.getsitepackages():
            print(f"  Checking: {path}")
            if (path / "rembg").exists():
                print(f"  ✓ Found rembg in: {path}")
            if (path / "rembg-rembg").exists():
                print(f"  ✓ Found rembg-rembg in: {path}")
    except Exception as e:
        print(f"Error checking site-packages: {e}")

    return False


def check_python_path():
    """Check Python path"""
    print("\n=== Python path ===")
    for path in sys.path:
        print(f"  {path}")


def main():
    print("Debugging rembg installation...")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")

    check_pip_packages()
    check_rembg_import()
    check_python_path()

    print("\n=== Recommendations ===")
    print("If rembg is not working:")
    print("1. Try: pip install --upgrade rembg")
    print("2. Try: pip install --force-reinstall rembg")
    print("3. Check if you're in the right virtual environment")
    print("4. Try: python -m pip install rembg")


if __name__ == "__main__":
    main()
