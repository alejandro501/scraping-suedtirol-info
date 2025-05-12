import subprocess
import sys
import logging

# Set up a logger
logger = logging.getLogger("startup")
logging.basicConfig(level=logging.INFO)

def ensure_dependencies():
    """Check and install dependencies using Python 3.11."""
    required_packages = ["requests", "beautifulsoup4", "lxml"]

    for package in required_packages:
        try:
            # Try to import the package to see if it's installed
            __import__(package)
        except ImportError:
            logger.info(f"Package {package} not found. Installing...")
            # Install the package if not found
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"Package {package} installed successfully.")

if __name__ == "__main__":
    ensure_dependencies()
