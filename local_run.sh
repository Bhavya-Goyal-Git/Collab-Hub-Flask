echo "Welcome to Collab Hub Run..."

SCRIPT_DIR=$(dirname "$(realpath "$BASH_SOURCE")")
VIRTUAL_ENVIRONMENT_DIRECTORY="$SCRIPT_DIR/venv"
DATABASE_DIRECTORY="$SCRIPT_DIR/instance"

if [ -d "$VIRTUAL_ENVIRONMENT_DIRECTORY" ]; then
    source "venv/Scripts/activate"
    if [ -d "$DATABASE_DIRECTORY" ]; then
        echo "Database Already exists..."
    else
        echo "Database for COLLAB HUB not found.."
        echo "Creating and setting up the DATABASE..."
        python dbmaker.py
        if [ $? -eq 0 ]; then
        echo "DATABASE Setup Completed Successfully!!"
        else
        echo "Could not setup the DATABASE..."
        exit 1
        fi
    fi
else
    echo "Virtual environment Not Found!!! Run local_setup.sh first!!"
    exit 1
fi

echo "Running Collab Hub on port 5000 now!...."
python run.py