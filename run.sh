cd TRACIE-GUI
trap "echo 'Stopping all processes...'; kill 0; exit" SIGINT
node server.js &
cd OpenLayerMap
npx vite build
cd ..
python TRACIE-GUI.py &
wait
