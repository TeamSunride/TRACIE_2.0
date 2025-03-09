import { WebSocketServer } from 'ws';

//NEW START
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
// NEW END

//==============================================
const wss = new WebSocketServer({ port: 7000 });
let mapClient = null;  // Track the MAIN.JS client

let sendCounter = 0;
let last_packet_rec_time = 0;
const map_update_per_sec = 1;                        // Adjust how often the map plots a coordinate
const send_rate = map_update_per_sec / 0.25;        //Average 4 messages per second.          

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
        // Updating groundAltitude
        if (messageStr.startsWith("GROUND_ALTITUDE:")) {
            //console.log("[SERVER] Received update:", messageStr);
            const parts = messageStr.split(":");
            const groundAltitude = parseFloat(parts[1]);                             // Remove GROUND_ALTITUDE: part, parse buffer into float
            const groundAltitudeMessage = JSON.stringify({groundAltitude});          // Send as a JSON object wth the property groundAltitude
            //console.log("[SERVER] Ground altitude update sent:", groundAltitudeMessage);
            mapClient.send(groundAltitudeMessage);
        }

        // Sending data stream
        const data_received = cleanArray(message);                      
        //console.log("[SERVER] Message received:", data_receiclved);     // Should receive: ['lon','lat','altitude','radio_state']
        if (data_received[3] != "0") {return;}      //Skip corrupted packets (radio_state = "1")

        var currentTime = new Date().getTime() / 1000;
        if (last_packet_rec_time != 0) {
            var time_difference = currentTime - last_packet_rec_time;
        }
        
        sendCounter += 1;
        last_packet_rec_time = currentTime;

        if (sendCounter == send_rate || time_difference > 10) {
            const data_send = JSON.stringify(data_received);
            mapClient.send(data_send);              //Send data to main.js (OpenLayer map)
            sendCounter= 0; // Reset sendCounter
        }
        else {          //Skip sending good packet
            return;
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
    wss.close(() => {
        console.log("[SERVER] Server closed.");
        process.exit(0);
    });
});

function cleanArray(data) {
    const data_array = data.toString().trim().split(",");
    return data_array;
}


//NEW START
app.post('/save-data', (req, res) => {
    const { rocketData, groundAltitude, currentLocation, fileName } = req.body;
  
    if (!fileName) {
      return res.status(400).send('File name is required');
    }
  
    const filePath = join(logFilesMapFolder, fileName);
  
    const dataToSave = {
      rocketData,
      groundAltitude,
      currentLocation,
    };
  
    fs.writeFile(filePath, JSON.stringify(dataToSave, null, 2), (err) => {
      if (err) {
        console.error('Error saving data:', err);
        return res.status(500).send('Failed to save data');
      }
      console.log(`Data saved to ${filePath}`);
      res.send('Data saved successfully');
    });
  });
  
  app.get('/load-data', (req, res) => {
    const fileName = req.query.file;
  
    if (!fileName) {
      return res.status(400).send('File name is required');
    }
  
    const filePath = join(logFilesMapFolder, fileName);
  
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
      res.json(files);
    });
  });
  
  // Start the HTTP server
  server.listen(port, () => {
    console.log(`[SERVER] Data-saving HTTP server running on http://localhost:${port}`);
  });
  
  process.on('SIGINT', () => {
    wss.close(() => {
      console.log("[SERVER] Server closed.");
      process.exit(0);
    });
  });
  

//NEW END