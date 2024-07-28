echo "Welcome to Local Setup For Collab Hub.."

SCRIPT_DIR=$(dirname "$(realpath "$BASH_SOURCE")")
VIRTUAL_ENVIRONMENT_DIRECTORY="$SCRIPT_DIR/venv"

if [ -d "$VIRTUAL_ENVIRONMENT_DIRECTORY" ]; then
    echo "Virtual environment directory already exists."
    exit 0
else
    echo "Virtual environment directory does not exist, creating it now...."
    python -m venv venv
    if [ $? -eq 0 ]; then
        echo "Virtual environment created successfully in 'venv'."
    else
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

echo "Activating the virtual environment...."
source "venv/Scripts/activate"

REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing packages from 'requirements.txt'..."
    pip install -r "$REQUIREMENTS_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Packages installed successfully..."
    else
        echo "Failed to install packages."
        deactivate
        exit 1
    fi
else
    echo "'requirements.txt' not found."
    deactivate
    exit 1
fi

deactivate
echo "Setup Completed Successfully..."