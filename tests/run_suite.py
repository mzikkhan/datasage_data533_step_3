import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def run_suite():
    root_dir = Path.cwd()
    src_dir = root_dir / "src"
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH", "")

    print(f"Starting Test Suite...")
    print(f"Source Directory: {src_dir}")

    omit_flags = "*/tests/*,*/test_*.py,*/__init__.py,*/retrieval/*,*/ingestion/loaders.py"
    
    cmd = [
        sys.executable, "-m", "coverage", "run",
        f"--omit={omit_flags}",
        "--source=src",
        "-m", "pytest",
        "tests",
        "-v" 
    ]

    # 3. Run the Tests
    print("\n" + "="*50)
    print("RUNNING TESTS via Coverage...")
    print("="*50)
    
    result = subprocess.run(cmd, env=env)

    print("\n" + "="*50)
    print("GENERATING REPORTS...")
    print("="*50)

    subprocess.run([sys.executable, "-m", "coverage", "report", "-m"], env=env)
    subprocess.run([sys.executable, "-m", "coverage", "html"], env=env)

    print("\nDone! Check 'htmlcov/index.html' for the visual report.")
    

    if result.returncode != 0:
        print("\nSOME TESTS FAILED. Please check the output above.")
    else:
        print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    run_suite()