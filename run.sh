cd TRACIE-GUI
trap "echo 'Stopping all processes...'; kill 0; exit" SIGINT
export $(grep -v '^#' .env | xargs)
node server.js &
cd OpenLayerMap
npx vite build
cd ..
if command -v python &>/dev/null; then
    python TRACIE-GUI.py &
elif command -v python3 &>/dev/null; then
    python3 TRACIE-GUI.py &
else
    echo "Error: Python is not installed." >&2
    exit 1
fi
wait
