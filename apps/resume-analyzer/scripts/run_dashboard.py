import subprocess
import os

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))
    cmd = ["uv", "run", "streamlit", "run", "apps/resume-analyzer/src/apps/resume_analyzer/frontend/app.py", "--server.port", "8501"]
    subprocess.run(cmd)
