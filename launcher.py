"""
Cross-platform orchestrator to launch all Theremin microservices.
"""
import subprocess
import os
import platform
import time

def get_venv_python(service_dir):
    """Returns the OS-correct path to the virtual environment Python executable."""
    if platform.system() == "Windows":
        return os.path.join(service_dir, "venv", "Scripts", "python.exe")
    return os.path.join(service_dir, "venv", "bin", "python")

def main():
    print("Starting Theremin Cluster...")
    
    # 1. Start Go Action Service
    action_proc = subprocess.Popen(
        "go run cmd/server/main.go",
        cwd="action-service",
        shell=True
    )
    time.sleep(2)
    
    # 2. Start Movement Service
    movement_proc = subprocess.Popen(
        [get_venv_python("movement-service"), "main.py"],
        cwd="movement-service"
    )
    
    # 3. Start Audio Service
    audio_proc = subprocess.Popen(
        [get_venv_python("audio-service"), "main.py"],
        cwd="audio-service"
    )

    try:
        print("\nAll services running. Press Ctrl+C to terminate everything.")
        # Infinite loop to keep the launcher alive and monitoring
        while True:
            time.sleep(1)
            
            # If the action server crashes, shut down cluster
            if action_proc.poll() is not None:
                print("\nERROR: Action Service crashed! Shutting down cluster...")
                break
                
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Shutting down cluster...")
    finally:
        # Graceful shutdown of all processes
        action_proc.kill()
        movement_proc.kill()
        audio_proc.kill()

if __name__ == "__main__":
    main()