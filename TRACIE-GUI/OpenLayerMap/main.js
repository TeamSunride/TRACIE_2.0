import './style.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile.js';
import { toLonLat, fromLonLat } from 'ol/proj.js';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import XYZ from 'ol/source/XYZ';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { Style, Icon, Circle as CircleStyle, Fill, Stroke} from 'ol/style';
import { icons } from './icons';
import { Mojave_Layers, MACH_X_Layers /* MRC_Layers EARS_Layers */} from './offlineMap';
import LayerGroup from 'ol/layer/Group.js';

const defaultLocation = {       // Set Mach-X as default location   
  name: 'MACH-X',
  lon: -5.687638,
  lat: 55.434629, 
  zoomSize: 16.8,
  minZoomSize: 14.5,
  maxZoomSize: 19,
};

// ==== SET UP EVERYTHING ====
let groundAltitude = 0;
let flightStartTime = new Date();
let currentFileName = '';
let fileTimestamp = '';
let selectedPlotCoords = '';
let isNewFlight = true;
let autosaveEnabled = false;
let autosaveIntervalId = null;
const autosaveInterval = 5 *1000;   // 5s
let currentLocation = defaultLocation;
let centerCoords = fromLonLat([currentLocation.lon, currentLocation.lat]);
let dotStyleSet = getDotStyleSet(defaultLocation.name);
//const launchTime = Date.now() / 1000;      //in seconds. need apply formatTimeLater use for onHover: T+ X seconds

//=== MAP INITIALISATION ===
const token = 'pk.eyJ1Ijoicm9ib3NhbTIwMDMiLCJhIjoiY2x3b3dkZzllMmN4bDJpcGZ3YTM5Y2YzOSJ9.qw98dr1XT293FplEQ-ToYQ';
const tileurl = `https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=${token}`;

// ==== PLOTTING STUFF ON MAP ====
//=== Static Marker Features ====
let centerMarker = new Feature({geometry: new Point(centerCoords)});

const jokeCoords = [                      //Graves. Add KAlpha.
  [-5.693629, 55.436442, 'Boomerang','Boomerang Grave'],
  [-5.698946, 55.432405, 'Shawarma', 'Shawarma Grave'],
  [-117.843853, 35.331388, 'Fintans_Corner', 'Fintan\'s Corner'],
];

const jokeRocketMarker = jokeCoords.map(coord => {
  const jokeName = coord[2]; // Extract name
  const jokeDesc = coord[3];
  const feature = new Feature({
    geometry: new Point(fromLonLat([coord[0], coord[1]])),
  });
  feature.set('jokeName', jokeName);   // Set name and description property
  feature.set('jokeDesc', jokeDesc);
  return feature;
});

//=== VECTOR SOURCES ===
const centerVectorSource = new VectorSource({features: [centerMarker]});
const rocketVectorSource = new VectorSource({features: []});
const jokeVectorSource = new VectorSource({features: jokeRocketMarker});

// === MARKER STYLES ===
const centerMarkerStyle = new Style({
  image: new Icon({
    anchor: [0.5, 1],
    src: `./icon_assets/centerMarker.png`,
    scale: 0.08, 
  })
});

let total = rocketVectorSource.getFeatures().length;        // Get colours dynamically

const rocketMarkerStyle = (index, total, dotStyleSet) => {
  const { radius, color } = getDotStyle(index, total, dotStyleSet);    // Get radius and colour dynamically
  return new Style({
    image: new CircleStyle({
      anchor: [0.5, 0.5],
      radius,
      fill: new Fill({
        color,
      }),
      stroke: new Stroke({
        color: 'black',
        width: 0.5,
      }),
    }),
  });
};

jokeRocketMarker.forEach(marker => {
  const jokeName = marker.get('jokeName');
  const jokeMarkerStyle = new Style({
    image: new Icon({
      anchor: [0.5, 1],
      src: getJokeMarker(jokeName),   // Get image by jokeName
      scale: 0.05,
    }),
  });
  marker.setStyle(jokeMarkerStyle);
});

// === LAYERS ===
const onlineLayer = new TileLayer({
  source: new XYZ({
    url: tileurl,
  }),
  preload: 30,
  cacheSize: 512
});

const centerVectorLayer = new VectorLayer({
  source: centerVectorSource,
  style: centerMarkerStyle,
});

const rocketVectorLayer = new VectorLayer({
  source: rocketVectorSource,
  style: rocketMarkerStyle,
});

const jokeVectorLayer = new VectorLayer({
  source: jokeVectorSource,
});

// ==== SET Z-INDEXES ==== 
rocketVectorLayer.setZIndex(2);            // Layers from top to bottom
centerVectorLayer.setZIndex(1);
jokeVectorLayer.setZIndex(1);

// ==== MAP ====
const map = new Map({
  target: 'map',
  layers: [
    onlineLayer,
    centerVectorLayer,
    rocketVectorLayer,
    jokeVectorLayer,
    //MRC_Layers,     // Layer groups
    //EARS_Layers,
    Mojave_Layers,
    MACH_X_Layers,
  ],
  view: new View({
    center: fromLonLat([currentLocation.lon, currentLocation.lat]),
    zoom: currentLocation.zoomSize,
    minZoom: currentLocation.minZoomSize,
    maxZoom: currentLocation.maxZoomSize
  }),
  canvasOptions: {
    willReadFrequently: true,
  },
});
onlineLayer.setVisible(false);        // Off until shown to be online

checkConnectivity(currentLocation);

connectWebSocket(map);                 // Start the WebSocket connection and plotting coords
const connectionStatusMessage = document.getElementById('status-message');
const locationButton = createLocationButton(map);
locationButton.textContent = `Current Location: ${defaultLocation.name}`;
createPlotPopup(map);
createStartNewMapButton(map);
createLoadOldFileButton(map);
createAutosaveButton();
createZoomLevelShow();
createCoordSelectShow();
createRecenterButton();





// === WEBSOCKET SERVER ===
function connectWebSocket(map) {       //Everything that matters with getting data from server.js
  const socket = new WebSocket("ws://localhost:7000");

  socket.onopen = function () {
    console.log("[MAIN.JS] Connected to WebSocket server!");
    socket.send("ready");         
  };

  socket.onmessage = function (event) {     //Event listener for when server.js sends a message containing data
    //console.log("[MAIN.JS] Raw message received:", event.data);
    try {
      const data = JSON.parse(event.data);
      
      if (data.groundAltitude !== undefined) {        // Receive a groundAltitude update
        groundAltitude = data.groundAltitude;
        console.log("[CLIENT] Received Ground altitude update:", groundAltitude);
        updateMarkerAltitudes(map);                        // Update all true altitude of previous points, refresh map
      }

      else {              
        if (data.isFinal)  {                           // TRACIE Connection loss - last packet sent >3s ago
          updateConnectionStatus('red');              // Plot last received data
          push2rocketCoords(data.packet_data);
          //console.log("[MAIN.JS] RED MESSAGE RECEIVED! Received final packet before disconnect");
          return;
        }
        else if (data.isWaitingGPSFix) {                // TRACIE connected but not accurate GPS
          updateConnectionStatus('yellow');           // Plot last received data
          //console.log("[MAIN.JS] YELLOW MESSAGE RECEIVED! Packet not plotted");
          return;
        }
        else {
          updateConnectionStatus('green');             // Set status-message to green
          push2rocketCoords(data);
        }
      }
    }

    catch (e) {
      console.error("[MAIN.JS] Error parsing data:", e);
    }
  };
  
  socket.onerror = function (error) {
      console.error("[MAIN.JS] WebSocket Error:", error);
  };

  socket.onclose = function () {                         //When websocket server is closed while map is running
      console.warn("[MAIN.JS] WebSocket Disconnected! Retrying in 5...");
      setTimeout(connectWebSocket, 5000);
  };
}

function push2rocketCoords(data) {
  try {
    const [lat, lon, alt] = data.map(Number);                // Convert string to numbers
    const coordTime = getCurrentTime();
    const trueAltitude = alt - groundAltitude;               //Adjust for groundAltitude update

    const rocketMarker = new Feature({                      // Create new feature for rocket marker
      geometry: new Point(fromLonLat([lon, lat])),});
    rocketMarker.set('longitude', lat);
    rocketMarker.set('latitude', lon);
    rocketMarker.set('raw_altitude', alt.toFixed(2));
    rocketMarker.set('true_altitude', trueAltitude.toFixed(2));      // Set altitude & timeStamp property
    rocketMarker.set('timeStamp', coordTime);

    rocketVectorSource.addFeature(rocketMarker);            // Add new feature to vector source for dynamic plotting
    assignMarkerColours(rocketVectorSource);                // Apply dynamic colour styling to each rocket marker

  }
  catch (e) {
    console.error("[MAIN.JS] Error processing data:", e);
  }
}

// ===== MARKER PLOT STYLING =====
function assignMarkerColours(rocketVectorSource) {                //Apply colour dynamically by when it was plot
  const features = rocketVectorSource.getFeatures();
  const total = features.length;
  
  features.sort((a, b) => {                                       // Sort plots chronologically
    const timeA = a.get('timeStamp');
    const timeB = b.get('timeStamp');
    return timeA.localeCompare(timeB);
    //console.log("[MAIN.JS] Comparing:", timeA, "and", timeB);
  });

  features.forEach((feature, idx) => {                            // Update styles for all features
    const featureIndex = idx + 1;
    const featureTotal = total;
    feature.setStyle(rocketMarkerStyle(featureIndex, featureTotal, dotStyleSet));
    //console.log("[MAIN.JS] DEBUG TimeStamp:", feature.get('timeStamp'), "Feature Index:", featureIndex, "Total:", featureTotal, "FeatureRatio:", featureIndex/featureTotal);
  });
}

function getDotStyleSet(location) {
  //DEFAULT COLOR PALETTE [MRC, EARS, MACH-X, DIAMOND]
  const dotStyleSetDefault = [                          //HSL: Hue, saturation, lightness
    { color: 'hsl(240, 5%, 70%)', radius: 3},         //Earliest plot
    { color: 'hsl(190, 20%, 60%)', radius: 3},
    { color: 'hsl(205, 70%, 50%)', radius: 4},  
    { color: 'hsl(210, 100%, 50%)', radius: 5},       //Most recent plot
  ]
  //MOJAVE COLOR PALETTE        better visibility over light background
  const dotStyleSetMojave = [
    { color: 'hsl(225, 100%, 64.00%)', radius: 3},
    { color: 'hsl(221, 100%, 50%)', radius: 3},  
    { color: 'hsl(240, 100%, 65%)', radius: 4},  
    { color: 'hsl(240, 70%, 50%)', radius: 5},
  ]

  if (location === 'Mojave') { 
    return dotStyleSetMojave;
  }
  else { 
    return dotStyleSetDefault;
  }
}

function getDotStyle(index, total, dotStyleSet) {
  // Fixed dot Styles
  const dotStyle_Red = { color: 'hsl(0, 100%, 50%)', radius: 5};

  var ratio = index/total;

  if (ratio < 0.3) {return dotStyleSet[0];}              // Return the Xth element in the dotStyleSet array
  else if (ratio >= 0.3 && ratio < 0.55) {return dotStyleSet[1];}
  else if (ratio >= 0.55 && ratio < 0.85) {return dotStyleSet[2];}
  else if (ratio >= 0.85 && ratio < 1) {return dotStyleSet[3];}
  else if (total === 0 || ratio === 1) {return dotStyle_Red;}      //Default & latest points are red
}

function getJokeMarker(jokeName) {          //Custom gravestones coming soon...
  if (jokeName == `Fintans_Corner`) { 
    return `./icon_assets/dangerous_bend.png`;
  }
  else {
      return `./icon_assets/graveMarker.png`;
  }
}

function updateMarkerAltitudes(map) {                     //Update previous plots with new groundAltitude
  const features = rocketVectorSource.getFeatures();
  features.forEach(feature => {
      const alt = feature.get('raw_altitude');
      const trueAltitude = alt - groundAltitude;
      feature.set('true_altitude', trueAltitude.toFixed(2));
  });
  map.render();                           // Refresh the map to reflect changes
}

// ==== CREATE HTML ELEMENTS, BUTTONS AND ACTIONS ====
function createPlotPopup(map) {
  const existingPopup = document.querySelector('.popup');
  if (existingPopup) {
    existingPopup.remove();
  }

  const popup = document.createElement('div');
  popup.className = 'popup';
  document.body.appendChild(popup);

  let popup_hoverTimeout;
  let isPopupVisible = false;

  map.on('pointermove', function (event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
      return feature;
    });

    if (feature) {
      if (popup_hoverTimeout) {
        clearTimeout(popup_hoverTimeout);
      }

      setTimeout(() => {
        const coordinates = feature.getGeometry().getCoordinates();
        const pixel = map.getPixelFromCoordinate(coordinates);

        // Handle rocket markers
        if (feature.get('true_altitude') !== undefined && feature.get('timeStamp') !== undefined) {
          const altitude = feature.get('true_altitude');
          const timeStamp = feature.get('timeStamp');
          const markerRadius = feature.getStyle().getImage().getRadius(); // Get the radius of the marker

          const popupWidth = popup.offsetWidth;
          const popupHeight = popup.offsetHeight;
          const offsetX = -popupWidth / 2;
          const offsetY = -popupHeight - markerRadius - 10;

          popup.style.display = 'block';
          popup.innerHTML = `Altitude: ${altitude}m<br>Time: ${timeStamp}`;
          popup.style.left = `${pixel[0]}px`;
          popup.style.top = `${pixel[1]}px`;
          popup.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
        popup.style.backgroundColor = '#fffef0';
        }
        // Handle joke markers
        else if (feature.get('jokeName') !== undefined) {
          const jokeDesc = feature.get('jokeDesc');
          popup.innerHTML = jokeDesc;
          popup.style.backgroundColor = '#9deaff';

          popup.style.display = 'block';
          popup.style.left = `${pixel[0]}px`;
          popup.style.top = `${pixel[1] + 60}px`;
          popup.style.padding = `5px`;
        } else {
          return; // Skip if neither rocketMarker nor jokeMarker
        }

        setTimeout(() => {
          popup.classList.add('visible');
        }, 10);

        isPopupVisible = true;
      }, 0);
    } else {
      if (isPopupVisible) {
        popup.classList.remove('visible');
        setTimeout(() => {
          popup.style.display = 'none';
          isPopupVisible = false;
        }, 200);
      }
    }
  });

  map.on('click', function (event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
      return feature;
    });

    if (feature && feature.get('true_altitude') !== undefined && feature.get('timeStamp') !== undefined) {
      selectedPlotCoords = `${feature.get('longitude')}, ${feature.get('latitude')}`;
      console.log('Plot coords = ', selectedPlotCoords);
      updateCoordSelectShow();
    }
  });

  map.on('pointermove', updateCursor);

  function updateCursor(event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
      return feature;
    });
    map.getTargetElement().style.cursor = feature ? 'pointer' : '';
  }
}

function createLocationButton(map) {                          // Location Selection Menu
  const currentLocationWrapper = document.getElementById('location-wrapper');
  const locationButton = document.getElementById('location-button');
  const locationDropdown = document.getElementById('location-dropdown');
  const locationOptions = document.querySelectorAll('.location-option');

  locationButton.addEventListener('click', () => {                                      // Show/hide the dropdown when the button is clicked
    locationDropdown.style.display = locationDropdown.style.display === 'block' ? 'none' : 'block';
  });

  locationOptions.forEach(option => {                                   // Handle location selection
    option.addEventListener('click', () => {
      const newLocation = {                                              // Update the current location
        name: option.getAttribute('data-name'),
        lon: parseFloat(option.getAttribute('data-lon')),
        lat: parseFloat(option.getAttribute('data-lat')),
        zoomSize: parseFloat(option.getAttribute('data-zoom')),
        minZoomSize: parseFloat(option.getAttribute('data-minZoom')),
        maxZoomSize: parseFloat(option.getAttribute('data-maxZoom')),
      };
      updateMapView(newLocation, map);

      checkConnectivity(newLocation);
      
      centerCoords = fromLonLat([newLocation.lon, newLocation.lat]);
      
      if (newLocation.name !== currentLocation.name) { 
        saveDataToBackend();
        rocketVectorSource.clear(); 
        currentLocation = newLocation;
        generateNewLogFile();
      }
      else {
        isNewFlight = false;            // To not generate new file
        saveDataToBackend();
      }
      locationDropdown.style.display = 'none';          // Hide the dropdown
    });
  });

  document.addEventListener('click', (event) => {                       // Close the dropdown if the user clicks outside of it
    if (!event.target.closest('#location-selector')) {
      locationDropdown.style.display = 'none';
    }
  });
  return locationButton;
}

function updateMapView(currentLocation, map) {              // Update map view. Used by Location Selection Menu, Start-New-Map, & Load-Old-File
  const newCenterCoords = fromLonLat([currentLocation.lon, currentLocation.lat]);
  map.getView().setCenter(newCenterCoords);                                           // Update the map view, center marker, dotsStyle, & Location Select button text
  map.getView().setZoom(currentLocation.zoomSize);
  map.getView().setMinZoom(currentLocation.minZoomSize);
  map.getView().setMaxZoom(currentLocation.maxZoomSize);

  centerCoords = newCenterCoords;
  centerMarker.getGeometry().setCoordinates(newCenterCoords);
  centerVectorSource.changed();
  dotStyleSet = getDotStyleSet(currentLocation.name);

  locationButton.textContent = `Current Location: ${currentLocation.name}`;
}

function createStartNewMapButton(map) {
  document.getElementById('start-new-map-button').addEventListener('click', () => {
    saveDataToBackend();
    rocketVectorSource.clear();         // Clear the current map, ground altitude, location => MRC
    groundAltitude = 0;
    updateMapView(currentLocation, map);        // Update map center and views
    generateNewLogFile();
  });
}

function createLoadOldFileButton(map) { 
  document.getElementById('file-button').addEventListener('click', () => {
    const fileDropdown = document.getElementById('file-dropdown');
    fileDropdown.style.display = fileDropdown.style.display === 'block' ? 'none' : 'block';
  });

    // LOAD-OLD-FILE Button. Toggle the scroll menu
  document.getElementById('load-old-file-button').addEventListener('click', () => {
    const fileList = document.getElementById('file-list');
    fileList.style.display = fileList.style.display === 'block' ? 'none' : 'block';
  });

  // Loading a file from the scroll menu          // async prob move out if issue.
  document.getElementById('file-list').addEventListener('click', async (event) => {
    const selectedFile = event.target.textContent;
    //saveDataToBackend();          // this doesn't work
    if (selectedFile) {
      rocketVectorSource.clear();
      await loadDataFromBackend(selectedFile, map);
    }
  });

  document.getElementById('load-old-file-button').addEventListener('click', async () => {
    const dropdown = document.getElementById('load-file-dropdown');
    const selectedFile = dropdown.value;
    saveDataToBackend();
    if (selectedFile) {
      rocketVectorSource.clear();
      await loadDataFromBackend(selectedFile, map);
    }
  });
}

function createAutosaveButton() { 
  const autosaveButton = document.getElementById('autosave-button');
  updateAutosaveButton();

  autosaveButton.addEventListener('click', () => {
    autosaveEnabled = !autosaveEnabled;
    updateAutosaveButton();
  });
}

function updateAutosaveButton() {
  const autosaveButton = document.getElementById('autosave-button');

  if (autosaveEnabled) {                                  // Autosave ON
    autosaveButton.textContent = 'Autosave ON';
    autosaveButton.style.backgroundColor = '#009024';
    saveDataToBackend();                                  // Autosave the instant the button is on

    if (autosaveIntervalId) {                             // Reset time interval
      clearInterval(autosaveIntervalId);
    }
        autosaveIntervalId = setInterval(() => {
      saveDataToBackend();
    }, autosaveInterval);
  }
  else {                                                  // Autosave OFF
    autosaveButton.textContent = 'Autosave OFF';
    autosaveButton.style.backgroundColor = '#800000';
    
    if (autosaveIntervalId) {
      clearInterval(autosaveIntervalId);
      autosaveIntervalId = null;
    }
  }
}

function createZoomLevelShow() { 
  const zoomLevelShow = document.getElementById('zoom-show');
  updateZoomLevelShow();
}

function updateZoomLevelShow() { 
  const zoomLevelShow = document.getElementById('zoom-show');
  const currentZoom = map.getView().getZoom();
  zoomLevelShow.textContent = `Zoom: ${currentZoom.toFixed(2)}`;
}
map.getView().on('change:resolution', updateZoomLevelShow);

function createCoordSelectShow() { 
  const coordWrapper = document.getElementById('coord-wrapper');
  const coordSelectShow = document.getElementById('coord-show');
  const copyButton = document.getElementById('copy-button');
  copyButton.addEventListener('click', copyText);
  updateCoordSelectShow();
}

function updateCoordSelectShow() { 
  const coordWrapper = document.getElementById('coord-wrapper');
  const coordSelectShow = document.getElementById('coord-show');
  const copyButton = document.getElementById('copy-button');
  let plotCoords = null;
  if (selectedPlotCoords == '') { 
    plotCoords = 'Click on a plot to view its coordinates';
    coordSelectShow.style.fontStyle = 'italic';
    copyButton.style.visibility = 'hidden';
  }
  else { 
    plotCoords = selectedPlotCoords;
    coordSelectShow.style.fontStyle = 'normal';
    copyButton.style.visibility = 'visible';
    copyButton.textContent= 'Copy';
    copyButton.style.backgroundColor = '#78b2ff';
  }
  coordSelectShow.textContent = plotCoords;
}

function copyText() {
  const copyButton = document.getElementById('copy-button');
  const coordShow = document.getElementById("coord-show");
  const textToCopy = coordShow.textContent;

  if (textToCopy !== 'Click on a plot to view its coordinates') {
    navigator.clipboard.writeText(textToCopy);
    copyButton.textContent='Copied';
    copyButton.style.backgroundColor = '#6ae689';
  }
  else { 
    return;
  }
}

function createRecenterButton() { 
  const recenterButton = document.getElementById('recenter-button');
  recenterButton.addEventListener('click', panToCenter);
}

function panToCenter() {
    const view = map.getView();
    view.animate({
        center: centerCoords,
        duration: 1000,               // Animation time in ms
    });
  }

function updateConnectionStatus(status) {
  switch (status) { 
    case 'grey': 
      connectionStatusMessage.textContent = 'Tracie status: Not Connected';
      connectionStatusMessage.style.backgroundColor = '#b8b8b8';
      break;
    case 'yellow':
      connectionStatusMessage.textContent = 'Tracie status: Waiting for GPS fix...';
      connectionStatusMessage.style.backgroundColor = "#ffe138";
      break;
    case 'green':
      connectionStatusMessage.textContent = 'Tracie status: Connected';
      connectionStatusMessage.style.backgroundColor = "#26ff35";
      break;
    case 'red':
      connectionStatusMessage.textContent = 'Tracie status: CONNECTION LOSS';
      connectionStatusMessage.style.backgroundColor = "#ff7038";
      break;
    default:
      break;
  }
}

// ==== SAVE AND LOADING MAP DATA ====
function generateFileName(location) {                         // FIlename for map log files
  const now = new Date();
  const date = now.toISOString().split('T')[0];                     // YYYY-MM-DD
  const time = now.toTimeString().split(' ')[0].replace(/:/g, '-'); // HH-MM-SS

  fileTimestamp =  `${date}_${time}`
  currentFileName = `${location}_${fileTimestamp}`;
  return `${currentFileName}.json`;
}

function generateNewLogFile() { 
    isNewFlight = true;
    flightStartTime = new Date();                   // Reset timestamp

    const newFileName = generateFileName(currentLocation.name); 
    fileTimestamp = newFileName.split('_').slice(1,3).join('_').replace('.json', '');
    currentFileName = newFileName.replace('.json', '');

    saveDataToBackend();                            // Start new log file
}

async function saveDataToBackend() {                        // Save data to the backend as JSON  
  const features = rocketVectorSource.getFeatures();
  const rocketDataToSave = features.map(feature => ({
    coordinates: feature.getGeometry().getCoordinates(),
    raw_altitude: feature.get('raw_altitude'),
    true_altitude: feature.get('true_altitude'),
    timeStamp: feature.get('timeStamp'),
  }));

  const fileName = `${currentFileName}.json`;
  //const fileName = isNewFlight ? generateFileName(currentLocation.name) : `${currentFileName}.json`;     // If new flight, create new file. Else, save to current file.

  try {
    const response = await fetch('http://localhost:8000/save-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        rocketData: rocketDataToSave,
        groundAltitude: groundAltitude,
        currentLocation: currentLocation,
        fileName,
        fileTimestamp,
        isNewFlight,
      }),
    });

    if (isNewFlight) { 
      isNewFlight = false;
    }
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const message = await response.text();
    console.log(`[SAVE] Data saved successfully.`);
  } catch (error) {
    console.error('[SAVE] Error saving data:', error);
  }
}

async function loadDataFromBackend(fileName, map) {              // Load old data from the backend
  saveDataToBackend();
  try {
    const response = await fetch(`http://localhost:8000/load-data?file=${fileName}`);
    const data = await response.json();

    if (data.rocketData) {                                          // Keep the if (data.XXX) in case of loading an empty file
      const features = data.rocketData.map(data => {
        const rocketMarker = new Feature({
          geometry: new Point(data.coordinates),
        });
        const lonLat = toLonLat(data.coordinates);
        rocketMarker.set('latitude', lonLat[0]);   // longitude
        rocketMarker.set('longitude', lonLat[1]);  // latitude
        rocketMarker.set('raw_altitude', data.raw_altitude);
        rocketMarker.set('true_altitude', data.true_altitude);
        rocketMarker.set('timeStamp', data.timeStamp);
        return rocketMarker;
      });
      rocketVectorSource.addFeatures(features);
      assignMarkerColours(rocketVectorSource);
    }

    if (data.groundAltitude) {
      groundAltitude = parseFloat(data.groundAltitude);
    }
    if (data.currentLocation) {
      currentLocation = data.currentLocation;
      updateMapView(currentLocation, map);
      checkConnectivity(currentLocation);
    }

    createPlotPopup(map);
    console.log(`[LOAD] Data loaded successfully from ${fileName}`);
  }
  catch (error) {
    console.error('[LOAD] Error loading data:', error);
  }
}

async function populateFileList() {                                       // Populate the dropdown menu with save files
  try {
    const response = await fetch('http://localhost:8000/list-save-files');
    const files = await response.json();

    // Sort files by date in descending order
    const sortedFiles = files.sort((a, b) => {            // Extract date and time from filenames
      const dateTimeA = extractISODateTime(a);
      const dateTimeB = extractISODateTime(b);
      return dateTimeB.localeCompare(dateTimeA);                // Compare date strings directly (most recent first)
    });

    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';                                  // Clear the list

    // Populate the sorted file list
    sortedFiles.forEach(file => {
      const fileOption = document.createElement('div');
      fileOption.className = 'file-option';
      fileOption.textContent = file;
      fileOption.addEventListener('click', () => {                                // Highlight the selected file
        document.querySelectorAll('.file-option').forEach(option => {
          option.classList.remove('selected');
        });
        fileOption.classList.add('selected');
      });
      fileList.appendChild(fileOption);
    });

    console.log('[LOAD] File list populated');
  } catch (error) {
    console.error('[LOAD] Error fetching save files:', error);
  }
}

function getCurrentTime() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

function extractISODateTime(filename) {
  // Helper function to extract ISO date and time from filename
  return filename.split('_').slice(1).join('_').replace('.json', '');
}

// ==++ ON/OFFLINE MAP ACTIVATION ==+=
function checkConnectivity(currentLocation) {
  const isOffline = !navigator.onLine;
  console.log(isOffline ? "OFFLINE MODE" : "ONLINE MODE");

  // Toggle visibility
  onlineLayer.setVisible(!isOffline);
  //MRC_Layers.setVisible(isOffline && currentLocation.name == "MRC");
  //EARS_Layers.setVisible(isOffline && currentLocation.name == "EARS");
  Mojave_Layers.setVisible(isOffline && currentLocation.name == "Mojave");
  MACH_X_Layers.setVisible(isOffline && currentLocation.name == "MACH-X");

  // DEBUG
  console.log(`Online visible: ${onlineLayer.getVisible()}`);
  //  console.log(`MRC visible: ${MRC_Layers.getVisible()}`);
  //  console.log(`EARS visible: ${EARS_Layers.getVisible()}`);
  console.log(`Mojave visible: ${Mojave_Layers.getVisible()}`);
  console.log(`MACH_X visible: ${MACH_X_Layers.getVisible()}`);

}
window.onload = async function () {                          // Load the save file options when the map is opened
  populateFileList();                                                                                                       //console.log('[INIT] Page loaded and dropdown populated');
  updateConnectionStatus('grey');                      // TRACIE connection status until good package received
  generateNewLogFile();
};

window.addEventListener('beforeunload', saveDataToBackend);   // Save data when the browser is closed or refreshed
//window.addEventListener('pagehide', saveDataToBackend);     // For mobile/bfcache

//'https://upload.wikimedia.org/wikipedia/commons/a/a3/June_odd-eyed-cat.jpg'       //Fav placeholder image