import { WebSocketServer, WebSocket } from 'ws';

import express from 'express';
import { createServer } from 'http';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import cors from 'cors';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const server = createServer(app);
const port = 8000; // HTTP server on port 8000

const logFilesMapFolder = join(__dirname, '../TRACIE-GUI/OpenLayerMap/log_files_map');
//console.log("Log file save path to:", logFilesMapFolder);

// Create the log_files_map folder if it doesn't exist
if (!fs.existsSync(logFilesMapFolder)) {
  fs.mkdirSync(logFilesMapFolder, { recursive: true });
}

app.use(cors({                          // Enable CORS for all routes
  origin: 'http://localhost:4040',
  methods: ['GET', 'POST'],             // Allow only specific HTTP methods
  credentials: true,                   // Allow cookies and credentials
}));

app.use(express.json());

//==============================================
const wss = new WebSocketServer({ port: 7000 });
let mapClient = null;  // Track the MAIN.JS client
let data_received = null;
let hasSentRedAlert = false;

const map_update_per_sec = 1;                        // Adjust how often to plot coord on map
const send_rate = map_update_per_sec / 0.25;        //Average 4 messages per second.       
let sendCounter = 0;
let last_packet_rec_time = 0;   
const CONNECTION_TIMEOUT = 3;              // Send connection warning when no new packets after 3 secs

const inactivityChecker = setInterval(() => {                   // Check when TRACIE connection is lost and trigger red connection status
  let currentTime = new Date().getTime() / 1000;
  if (hasSentRedAlert == true || last_packet_rec_time == 0 || data_received == null) {
    return;   // If connection is lost and not yet reconnected, don't send redAlert
  }       
  if (currentTime - last_packet_rec_time > CONNECTION_TIMEOUT) {
    const redAlert = {                                    // Send last good packet with isFinal property
      packet_data: data_received,
      isFinal: true
    };
    mapClient.send(JSON.stringify(redAlert));
    hasSentRedAlert = true;
    sendCounter= 0;
  }
}, 2000);               // Check for inactivity every 2s

wss.on('connection', (ws) => {
  //console.log("[SERVER] WebSocket connected!");

  ws.on('message', (message) => {
    //console.log("[SERVER] Received message from client:", message.toString());
    const messageStr = message.toString();

    if (messageStr === "ready") {
        //console.log("[SERVER] MAIN.JS is ready!");
        mapClient = ws;      // Store the MAIN.JS client
        return;
    }

    // Check if safe to send data
    if (!mapClient) {
        console.warn("[SERVER] MAIN.JS client not ready. Data not sent.");      // Happens when map not open in browser
        return;
    }
    if (mapClient.readyState !== WebSocket.OPEN) {
        console.warn("[SERVER] MAIN.JS WebSocket is not open. Data not sent.");
        return;
    }
    
    // === FORWARD DATA FROM TRACIE_GUI.PY to MAIN.JS ===
    // Update groundAltitude
    if (messageStr.startsWith("GROUND_ALTITUDE:")) {
      //console.log("[SERVER] Received update:", messageStr);
      const parts = messageStr.split(":");
      const groundAltitude = parseFloat(parts[1]);                             // Remove GROUND_ALTITUDE: part, parse buffer into float
      const groundAltitudeMessage = JSON.stringify({groundAltitude});          // Send as a JSON object wth the property groundAltitude
      mapClient.send(groundAltitudeMessage);
      //console.log("[SERVER] Ground altitude update sent:", groundAltitudeMessage);
    }

    // ==== SENDING DATA STREAM ====
    data_received = cleanArray(message);                      //console.log("[SERVER] Message received:", data_received);     // Should receive: ['lon','lat','altitude','radio_state']
    if (data_received[4] != "0") {                            //Skip corrupted packets (radio_state = "1")
      return;
    }
    else if (data_received[3] == 0) {                       // GPS fix = 0, connected but not accurate GPS
      const yellowAlert = {
        packet_data: data_received,
        isWaitingGPSFix: true
      };
      mapClient.send(JSON.stringify(yellowAlert));
      sendCounter = 3;                                      // To send the next good packet immediately
      return;
    }

    // Good packets only 
    sendCounter += 1;                                       // Increment counter for every good packet
    hasSentRedAlert = false;                                // Enable inactivityChecker
    last_packet_rec_time = new Date().getTime() / 1000;

    if (sendCounter != send_rate) {                       
      return;
    }
    else {
      const data_send = JSON.stringify(data_received);
      mapClient.send(data_send);                            //Send data to main.js (OpenLayer map)
      sendCounter = 0;
    }
  })

  ws.on('close', () => {
    //console.log("[SERVER] Client disconnected");
    if (ws === mapClient) {
        mapClient = null;  // Clear the MAIN.JS client
    }
  });

  ws.on('error', (error) => {
    console.error("[SERVER] WebSocket error:", error);
  });
});

console.log("[SERVER] WebSocket server running on: ws://localhost:7000");

process.on('SIGINT', () => {
  clearInterval(inactivityChecker);
  wss.close(() => {
    console.log("[SERVER] Server closed.");
    process.exit(0);
  });
});

function cleanArray(data) {
  const data_array = data.toString().trim().split(",");                     //console.log("[SERVER] Data cleaned:", data_array);
  return data_array;
}


// ==== SAVING MAP DATA ====
let correct_fileTimestamp = '';

app.post('/save-data', (req, res) => {
  const { rocketData, groundAltitude, currentLocation, fileName, fileTimestamp, isNewFlight } = req.body;
  const filePath = join(logFilesMapFolder, fileName);

  if (isNewFlight) {                                     // If is new flight: update correct_fileTimestamp to save ONLY to the new file
    correct_fileTimestamp = fileTimestamp;
    console.log(`\nSaving data from date & time: ${correct_fileTimestamp}`);
  }

  if (correct_fileTimestamp && fileTimestamp !== correct_fileTimestamp) {                             // Solves issue of with randomly opening and logging to old files
    //console.warn(`Rejected save: Expected ${correct_fileTimestamp}, got ${fileTimestamp}`);         // If the fileTimestamp of the file currently opened doesn't match: ignore
    return res.status(400).json({ 
      error: "Timestamp mismatch",
      expected: correct_fileTimestamp,
      received: fileTimestamp
    });
  }

  fs.writeFileSync(filePath, JSON.stringify({rocketData,groundAltitude,currentLocation}, null, 2));   // Save the data
  console.log(`AUTOSAVE: Data saved to ${fileName}`);     // or ${filePath}
  res.send('Data saved successfully');
});

// ==== LOADING OLD DATA ====
app.get('/load-data', (req, res) => {
  const fileName = req.query.file;

  if (!fileName) {
    return res.status(400).send('File name is required');
  }

  const filePath = join(logFilesMapFolder, fileName);
    correct_fileTimestamp = fileName.split('_').slice(2).join('_').replace('.json', '');       // Update the  correct_fileTimestamp when loading old files 
    console.log(`\nLoading map data from: ${fileName}`);
    console.log('! NOTE: New data will not save to any files while an old file is open.\n  To save new data, start a new map or change location.');

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading data file:', err);
      return res.status(500).send('Failed to load data');
    }
    res.json(JSON.parse(data));
  });
}); 

app.get('/list-save-files', (req, res) => {
  fs.readdir(logFilesMapFolder, (err, files) => {
    if (err) {
      console.error('Error reading data folder:', err);
      return res.status(500).send('Failed to list save files');
    }
    const filteredFiles = files.filter(file => file !== '.gitkeep');    // Don't show .gitkeep"
    res.json(filteredFiles);
  });
});

// Start the HTTP server for saving data
server.listen(port, () => {
  console.log(`[SERVER] Data-saving HTTP server running on http://localhost:${port}`);
});

process.on('SIGINT', () => {
  wss.close(() => {
    console.log("[SERVER] Server closed.");
    process.exit(0);
  });
});