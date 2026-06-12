# Setup script for AI Workshop Systems
echo "Setting up virtual environment..."
python -m venv venv
venv\Scripts\Activate.ps1
echo "Installing dependencies..."
pip install -r requirements-lock.txt
echo "Setup complete."
