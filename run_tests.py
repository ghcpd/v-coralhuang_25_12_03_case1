import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    req = ROOT / "requirements.txt"
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req)])
    except subprocess.CalledProcessError:
        sys.exit(1)
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "tests"]))


if __name__ == "__main__":
    main()
