import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor

def run_backend():
    # Add the current directory to PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    subprocess.run([
        sys.executable, 
        "-m", 
        "uvicorn", 
        "main:app", 
        "--reload",
        "--host", 
        "0.0.0.0", 
        "--port", 
        "8000"
    ], env=env)

def run_frontend():
    os.chdir('frontend')
    subprocess.run(["npm", "run", "dev"])

def main():
    # Create __init__.py files if they don't exist
    backend_dirs = [
        'backend',
        'backend/competition_manager',
        'backend/auth_manager'
    ]
    
    for dir_path in backend_dirs:
        os.makedirs(dir_path, exist_ok=True)
        init_file = os.path.join(dir_path, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_backend)
        executor.submit(run_frontend)

if __name__ == "__main__":
    main() 