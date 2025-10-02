import PySide6

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QUrl, QThread
from PySide6.QtGui import QDesktopServices
from PySide6 import QtCore, QtWidgets
import Interface_ui
import sys
from fakeSerial import FakeSerial
import io
import time
import numpy as np
from configparser import *
import serial.tools.list_ports
import serial
import json
import asyncio
import websockets
from collections import deque
import os
import pyqtgraph as pg
import csv
from simplekml import Kml
import simplekml
import sys
import threading
from flask import Flask, send_from_directory

WS_PORT = os.environ.get("WS_PORT", "7000")
CLIENT_PORT = os.environ.get("CLIENT_PORT", "4040")

app = Flask(__name__)       # Initialize Flask app to run map
current_dir = os.path.dirname(os.path.abspath(__file__))             
bundled_dir = os.path.join(current_dir, 'OpenLayerMap', 'dist')         #Path to OpenLayers bundled HTML

# Flask: serve OpenLayer HTML and static files
@app.route('/map')
def serve_map():
    return send_from_directory(bundled_dir,'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(bundled_dir, filename)

def run_flask():
    app.run(debug=False, host='localhost', port= int(CLIENT_PORT))

# WEBSOCKET SERVER
class AsyncioThread(QThread):
    def __init__(self):
        super().__init__()
        self.ws = None 
        self.loop = None

    def run(self):                                  #Create an event loop that runs forever
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def send_message_to_websocket(self, data, message_type):           #Send data to websocket server
        uri = "ws://localhost:{}".format(int(WS_PORT))
        try:
            async with websockets.connect(uri) as ws:
                if message_type == "data_message":
                    data_selected = [data[0],data[1],data[2],data[3],data[9]]                   # Only send long, lat, alt, (GPS) fix, radio_state
                    data_send = ",".join(data_selected).replace(" ", "")
                    await ws.send(data_send)               # Send data as CSV string
                    #print(f"[GUI] Data sent.",data_send)
                elif message_type == "groundAltitude_message":
                    ground_altitude_send = f"GROUND_ALTITUDE:{data}"
                    await ws.send(ground_altitude_send)
                    #print(f"[GUI] Ground altitude sent: {data}")

        except Exception as e:
            print(f"[GUI] WebSocket Error: {e}")

    def send_message(self, data, message_type):                              #Schedules data sending in the asyncio loop
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.send_message_to_websocket(data, message_type), self.loop)
        else:
            print("[GUI] Warning: Event loop is not running.")


class TRACIE_GUI(QMainWindow, Interface_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(TRACIE_GUI, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("TRACIE-GUI")

        # ======= CHANGE DIRECTORY ======
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)        
        current_dir = os.path.dirname(script_dir)               #Always moves to /TRACIE directory
        os.chdir(current_dir)

        # ======= CONFIG ======
        self.config = ConfigParser()
        self.config_file_path = "./TRACIE-GUI/TRACIE_GUI_CONFIG.ini"
        self.config.read(self.config_file_path)

        # ====== SERIAL COMMS =======
        self.ports = serial.tools.list_ports.comports()
        self.selectedDevice = ""
        
        # ==== SELECT REAL/FAKE SERIAL ====
        self.ser_realfake = 1                 # 1 for REAL (TRACIE board connected). 0 for FAKE (fakeSerial.py)
        if (self.ser_realfake == 1):
            self.ser = None
        elif (self.ser_realfake == 0):
            self.ser = FakeSerial()         # For testing without TRACIE irl :)
        self.setupDeviceSelection()

        # Read the serial buffer using a QTimer
        self.serial_read_timer = QtCore.QTimer()
        self.serial_read_timer.timeout.connect(self.readSerial)
        self.serial_read_timer.start(50)        #50ms

        # Continuous update timer
        self.last_packet_rec_time = time.time()
        self.background_timer = QtCore.QTimer()
        self.background_timer.timeout.connect(self.continuous_update)    # Updates a whole bunch of things, that need to be updated somewhat regularly - avoids using QThreads.
        self.background_timer.start(100)        #100ms

        # ===== DATA and DISPLAY =====
            # Latest raw data field
        self.raw_data = []
        self.groundAltitude = 0      # For zero altitude button

        # CSV logging
        self.log_csv_base_path = "./TRACIE-GUI/log_files"
        self.log_csv_name = ""
        self.influx_log_name = ""
        self.setup_logging()


        # ========== Plots =========
        # What's the best way to do this? Live plotting with  a QGraph? or updating with matplotlib?
        self.times_seconds_map = {
            "-5s": 5,
            "-1m": 60,
            "-5m": 60*5,
            "-15m": 60*15,
            "-30m": 60*30,
            "-60m": 60*60,
        }
        self.plots_back_time = self.times_seconds_map[self.config["TRACIE"]["plots_time_selection"]]
        self.time_circular_buffer = deque(maxlen=self.times_seconds_map["-60m"]*4) # 4 samples per second, 60 minutes max time
        self.altitude_circular_buffer = deque(maxlen=self.times_seconds_map["-60m"]*4) # 4 samples per second, 60 minutes max time
        self.flightAltitudeGraphicsView.setBackground('w')
        self.pen = pg.mkPen(color=(0, 0, 255), width=5)
        self.flightAltitudeGraphicsView.plot(
            self.time_circular_buffer,
            self.altitude_circular_buffer,
            pen=self.pen
        )
        self.altitudeGraphTime = time.time()

        # ==== MAP ===
        self.user_location = [float(self.config['TRACIE']['user_latitude']), 
                              float(self.config['TRACIE']['user_longitude'])]
        self.good_packet_count = 0
        self.start_map()
        self.setup_plots()
        self.connect_handlers()

    def connect_handlers(self):
        self.deviceConnectButton.clicked.connect(self.connectDeviceButtonHandler)
        self.flightLatitudeLineEdit.editingFinished.connect(lambda: self.lineEdit_handler(self.flightLatitudeLineEdit, 'TRACIE', 'user_latitude'))
        self.flightLongitudeLineEdit.editingFinished.connect(lambda: self.lineEdit_handler(self.flightLongitudeLineEdit, 'TRACIE', 'user_longitude'))
            # Set the initial text of these line edits to the current config
        self.flightLatitudeLineEdit.setText(self.config['TRACIE']['user_latitude'])
        self.flightLongitudeLineEdit.setText(self.config['TRACIE']['user_longitude'])
        self.flightPlotsTimeSelectionComboBox.currentIndexChanged.connect(self.plotsTimeSelectedComboBoxHandler)

        self.channel1Button.clicked.connect(self.channel1ButtonHandler)
        self.channel2Button.clicked.connect(self.channel2ButtonHandler)

        self.flightGoogleMapsButton.clicked.connect(self.googleMapsButtonHandler)
        self.exportKMLButton.clicked.connect(self.exportKMLButtonHandler)
        self.zeroAltitudeButton.clicked.connect(self.zeroAltitudeButtonHandler)

    def write_to_config(self):
        # Write the config to disk
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

    def setup_logging(self):
        time_string = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        print(time_string)
        self.log_csv_name = os.path.join(self.log_csv_base_path, "log" + time_string+ ".csv")
        # Replace backslashes with forward slashes
        self.log_csv_name = self.log_csv_name.replace("\\", "/")
        self.influx_log_name = os.path.join(self.log_csv_base_path, "influx_log", time_string+ ".csv")
        # Create the log files
        with open(self.log_csv_name, "w+") as f:
            f.write("Unix Time,Formatted Time,Latitude,Longitude,Altitude,Fix,SIV,Unixtime,RSSI,SNR,Freqerr,Radio State\n")
        # with open(self.influx_log_name, "w") as f:
        #     f.write("Latitude,Longitude,Altitude,Fix,SIV,Unixtime,RSSI,SNR,Freqerr,Radio State\n")

    def setup_plots(self):
        # Setup the log CSV combo box
        for key in self.times_seconds_map.keys():
            self.flightPlotsTimeSelectionComboBox.addItem(key)
        self.flightPlotsTimeSelectionComboBox.setCurrentText(self.config["TRACIE"]["plots_time_selection"])

#############  Config tab
    def setupDeviceSelection(self):
        # TODO: How can we make this update in real time, so that we can detect when a new device is plugged in?
        self.ports = serial.tools.list_ports.comports()
        self.deviceComboBox.clear()
        for port, desc, hwid in sorted(self.ports):
            # print(f"{port}: {desc} [{hwid}]")
            if hwid.startswith("USB"): # Filter out non-USB devices (bluetooth, etc.)
                # Extract PID and VID from hwid - example HWID: USB VID:PID=0483:5740 SER=206136A95131 LOCATION=1-2
                vidpid = hwid.split("VID:PID=")[1].split(" ")[0]
                vid = vidpid.split(":")[0]
                pid = vidpid.split(":")[1]
                # print("VID: " + vid + " PID: " + pid)
                if vid == "10C4": # Groundstation
                    st = port + ":" + "Groundstation:" + pid
                    self.deviceComboBox.addItem(st)
                    # print(st)
                elif vid == "0483": # Tracker
                    st = port + ": " + "Tracker: " + pid
                    self.deviceComboBox.addItem(st)
                    # print(st)
        # Read the current selected device
        self.deviceComboBox.currentIndexChanged.connect(self.deviceSelectedComboBoxHandler)
        self.deviceSelectedComboBoxHandler()

    def readSerial(self):
        if self.ser is not None and self.ser.isOpen():
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if line == "":
                    return
                # print(line)
                if line.startswith("[DATA]:"):
                    line = line.split(":")[1] # Remove the [DATA]: part
                    data = line.split(",")
                    #print(line)
                    asyncio_thread.send_message(data, message_type = "data_message")
                    latitude, longitude, altitude, fix, siv, max_altitude_m, rssi, snr, freqerr, radio_state = data
                    self.raw_data = data
                    self.logData()
                    if int(radio_state) == 0: # Only uncorrupted packets get displayed on the GUI
                        if fix != "0":
                            self.time_circular_buffer.append(time.time() - self.altitudeGraphTime)
                            self.altitude_circular_buffer.append(float(altitude))
                        self.good_packet_count += 1
                        self.updateFlightPage()
                    else:
                        self.last_packet_rec_time = time.time()         # We still want to know that we recieved _something_, so update the packet age.
                        self.continuous_update()
                
            except Exception as e:
                print(e)

    def updateFlightPage(self):
        # Update the labels
        self.flightLatitudeLabel.setText(self.raw_data[0])
        self.flightLongitudeLabel.setText(self.raw_data[1])
        altitude = float(self.raw_data[2])
        self.flightAltitudeLabel.setText(str(round(float(self.raw_data[2])-self.groundAltitude,3)))
        self.flightGPSFixLabel.setText(self.raw_data[3])
        self.flightSIVLabel.setText(self.raw_data[4])
        self.flightMaxAltitudeLabel.setText(str(round(float(self.raw_data[5])-self.groundAltitude,3)))
        self.flightRSSILabel.setText(self.raw_data[6])
        self.flightSNRLabel.setText(self.raw_data[7])
        
        # Calculate heading (from north) and elevation (from horizontal)
        # TODO: Update heading and elevation fields - ASK TOM DANVERS
        launch_site_ecef = lla2ecef(self.user_location[0], self.user_location[1], 600)
        current_ecef = lla2ecef(float(self.raw_data[0]), float(self.raw_data[1]), altitude)
        heading, elevation, _range = ecef2aer(launch_site_ecef, current_ecef)

        self.flightHeadingLabel.setText(str(round(heading, 1)))
        self.flightElevationLabel.setText(str(round(elevation, 1)))
        self.flightRangeLabel.setText(str(round(_range, 1)))

        self.last_packet_rec_time = time.time()

        self.update_altitude_graph()
    
    def update_altitude_graph(self):
        # Update the altitude plot
        # self.flightAltitudeGraphicsView.plot(self.time_circular_buffer, self.altitude_circular_buffer, pen=self.pen, clear=True)
        # Alter how much is shown depending on the selected time in the combo box
        if not self.time_circular_buffer or not self.altitude_circular_buffer:
            return

        if self.time_circular_buffer[-1] > self.plots_back_time:
            self.flightAltitudeGraphicsView.setXRange(self.time_circular_buffer[-1] - self.plots_back_time, self.time_circular_buffer[-1])
        else:
            self.flightAltitudeGraphicsView.setXRange(0, self.time_circular_buffer[-1])

        self.flightAltitudeGraphicsView.plot(self.time_circular_buffer,
                                                self.altitude_circular_buffer,
                                                pen=self.pen, clear=True)
        self.flightAltitudeGraphicsView.setTitle('Altitude vs Time')
        self.flightAltitudeGraphicsView.setLabel('left', 'Altitude', units='m')
        self.flightAltitudeGraphicsView.setLabel('bottom', 'Time from Launch', units='s')
        self.flightAltitudeGraphicsView.showGrid(x=True, y=True)

    def continuous_update(self):
        # update the flight package age
        self.flightPackageAgeLabel.setText(str(round(time.time() - self.last_packet_rec_time, 1)))

        # update the comports
        self.setupDeviceSelection()

    def logData(self):
        # Log the data to a file
        with open(self.log_csv_name, "a") as f:
            unixtime = time.time()
            formatted_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            f.write(str(unixtime) + ",")
            f.write(str(formatted_time) + ",")
            f.write(",".join(self.raw_data) + "\n")

    def start_map(self):
        url = "http://localhost:{}/map".format(int(CLIENT_PORT))       # Open map in local browser
        QDesktopServices.openUrl(QUrl(url)) 


# ========== HANDLERS ============ 
    def deviceSelectedComboBoxHandler(self):
        text = self.deviceComboBox.currentText()
        self.selectedDevice = text.split(":")[0]
        # print("Selected device: " + self.selectedDevice)

    def plotsTimeSelectedComboBoxHandler(self):
        text = self.flightPlotsTimeSelectionComboBox.currentText()
        self.config["TRACIE"]["plots_time_selection"] = text
        self.write_to_config()
        self.plots_back_time = self.times_seconds_map[text]

    def connectDeviceButtonHandler(self):
        # Connect to the selected device    # Open serial port
        try:
            self.ser = serial.Serial(self.selectedDevice, 115200, timeout=0.05) # 50ms timeout
        except Exception as e:
            print(e)
        if self.ser.isOpen():
            print("Connected to " + self.selectedDevice)
            self.connectionStatusResultLabel.setText("Connected to " + self.selectedDevice)
            self.altitudeGraphTime = time.time()
        else:
            print("Failed to connect to " + self.selectedDevice)
            self.connectionStatusResultLabel.setText("Disconnected")

    def lineEdit_handler(self, lineEditObject, config_section, config_parameter):
        # Write the lineEdit value to the config file
        # validate the input
        if lineEditObject.hasAcceptableInput():
            self.config[config_section][config_parameter] = lineEditObject.text()
            self.write_to_config()
        # else:
        #     self.error_label.setText('Invalid input: ' + lineEditObject.text())

    def browseFileDumpPathButtonHandler(self):
        # Open file dialog to select save path in the current save path
        self.save_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory to dump files in", self.config['TRACIE']['user_flash_dump_directory'])
        if self.save_path:
            self.configFlashDumpLocationLabel.setText(self.save_path)
            self.config['TRACIE']['user_flash_dump_directory'] = self.save_path
            self.write_to_config()
        else: 
            print('No path selected')
            return

    def retrieveFlashDataButtonHandler(self):
        pass # TODO

    def googleMapsButtonHandler(self):
        s1 = lat_long_to_string(float(self.raw_data[0]), float(self.raw_data[1]))
        s2 = self.raw_data[0]
        s3 = self.raw_data[1]
        base_path = f"https://www.google.com/maps/place/{s1}/@{s2},{s3},17z/"
        print(base_path)
        parsed_path = QUrl(base_path)
        if parsed_path.isValid():
            QDesktopServices.openUrl(parsed_path)
            print("OPENED THE LINK")

    def exportKMLButtonHandler(self):
       # Open the CSV file
        kml = Kml()
        time_col = 0
        lat_col = 2  # Column index for latitude
        lon_col = 3  # Column index for longitude
        alt_col = 4  # Column index for altitude

        # Define styles for the line and ground curtain
        ls = kml.newlinestring(name="TRACIE Flight Path")


        coordinates = []
        with open(self.log_csv_name, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            first_altitude = 0
            count = 0
            # Process each row in the CSV
            for row in reader:
                # Extract data from specified columns   
                name = row[time_col]
                latitude = float(row[lat_col])
                longitude = float(row[lon_col])
                altitude = float(row[alt_col]) - 550  # Add altitude
                # if count == 0:    
                #     first_altitude = altitude

                count += 1
                

                coordinates.append((longitude, latitude, altitude))
                # point = kml.newpoint(name=name, coords=[(longitude, latitude)])
            
            # line =  kml.newlinestring(name="Flight Path", coords=coordinates, line_style=line_style)
            # curtain = kml.newlinestring(name="Ground Curtain",
                                    
                                        # style=curtain_style)

                
        ls.coords = coordinates
        ls.altitudemode = simplekml.AltitudeMode.relativetoground
        ls.style.linestyle.color = "ff3c14dc"
        ls.style.linestyle.width = 3
        ls.polystyle.outline = 0
        ls.polystyle.color = "643c14dc"
        ls.extrude = 1
        kml.save("TRACIE" + str(time.time())+".kml")
        print(f"KML file created.")

    def zeroAltitudeButtonHandler(self):
        if len(self.raw_data) >= 3:
            self.groundAltitude = float(self.raw_data[2])
            self.zeroAltitudeButton.setEnabled(True) 
            self.updateFlightPage()
            asyncio_thread.send_message(str(self.groundAltitude), message_type="groundAltitude_message")
        else:
            self.zeroAltitudeButton.setEnabled(False)

    def channel1ButtonHandler(self):
        message = "CHANNEL1"
        self.ser.write(message.encode())

    def channel2ButtonHandler(self):
        message = "CHANNEL2"
        self.ser.write(message.encode())

def main(args=None):
    global asyncio_thread
    flask_thread = threading.Thread(target=run_flask)        # Start Flask in a separate thread
    flask_thread.daemon = True                               # Stop Flask thread stops when app exits
    flask_thread.start()

    app = QApplication(sys.argv)
    gui = TRACIE_GUI()
    
    asyncio_thread = AsyncioThread()  
    asyncio_thread.start()

    gui.show()
    sys.exit(app.exec())


def ecef2lla(x, y, z):
    # x, y and z are scalars or vectors in meters
    x = np.array([x]).reshape(np.array([x]).shape[-1], 1)
    y = np.array([y]).reshape(np.array([y]).shape[-1], 1)
    z = np.array([z]).reshape(np.array([z]).shape[-1], 1)

    a = 6378137
    e_sq = 6.69437999014e-3

    f = 1 / 298.257223563
    b = a * (1 - f)

    # calculations:
    r = np.sqrt(x ** 2 + y ** 2)
    ep_sq = (a ** 2 - b ** 2) / b ** 2
    ee = (a ** 2 - b ** 2)
    f = (54 * b ** 2) * (z ** 2)
    g = r ** 2 + (1 - e_sq) * (z ** 2) - e_sq * ee * 2
    c = (e_sq ** 2) * f * r ** 2 / (g ** 3)
    s = (1 + c + np.sqrt(c ** 2 + 2 * c)) ** (1 / 3.)
    p = f / (3. * (g ** 2) * (s + (1. / s) + 1) ** 2)
    q = np.sqrt(1 + 2 * p * e_sq ** 2)
    # RuntimeWarning: invalid value encountered in sqrt
    # handle invalid (negative?) input to sqrt input over poles
    sqrt_input = 0.5 * (a ** 2) * (1 + (1. / q)) - p * (z ** 2) * (1 - e_sq) / (q * (1 + q)) - 0.5 * p * (r ** 2)
    if np.any(sqrt_input < 0):
        print(sqrt_input)
    sqrt_input[sqrt_input < 0] = 0

    r_0 = -(p * e_sq * r) / (1 + q) + np.sqrt(sqrt_input)
    u = np.sqrt((r - e_sq * r_0) ** 2 + z ** 2)
    v = np.sqrt((r - e_sq * r_0) ** 2 + (1 - e_sq) * z ** 2)
    z_0 = (b ** 2) * z / (a * v)
    h = u * (1 - b ** 2 / (a * v))
    phi = np.arctan((z + ep_sq * z_0) / r)
    lambd = np.arctan2(y, x)

    return phi * 180 / np.pi, lambd * 180 / np.pi, h

def ecef2enu(a, b):
    # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ECEF_to_ENU
    lat, long, alt = ecef2lla(a[0], a[1], a[2])

    lat = lat.item() if isinstance(lat, np.ndarray) else lat
    long = long.item() if isinstance(long, np.ndarray) else long
    alt = alt.item() if isinstance(alt, np.ndarray) else alt

    lat, long, alt = float(lat), float(long), float(alt)

    slat = np.sin(np.radians(lat))
    slon = np.sin(np.radians(long))
    clat = np.cos(np.radians(lat))
    clon = np.cos(np.radians(long))

    enu = np.matmul(np.array([
        [- slat, clon, 0],
        [- slat * clon, - slat * clon, clat],
        [clat * clon, clat * slon, slat]
    ]), b - a)
    return enu

def enu2aer(enu):
    _range = np.linalg.norm(enu)
    azimuth = np.arctan2(enu[0], enu[1])
    elevation = np.arcsin(enu[2] / _range)

    return np.degrees(azimuth).item(), np.degrees(elevation).item(), _range.item()

def ecef2aer(a, b):
    return enu2aer(ecef2enu(a, b))

def aer2enu(azimuth, elevation, _range):
    """
    Convert azimuth, elevation and range to local East, North Up coordinates
    """
    cos_azimuth = np.cos(np.radians(azimuth))
    cos_elevation = np.cos(np.radians(elevation))
    sin_azimuth = np.sin(np.radians(azimuth))
    sin_elevation = np.sin(np.radians(elevation))

    enu = np.array([
        _range * cos_elevation * sin_azimuth,
        _range * cos_elevation * cos_azimuth,
        _range * sin_elevation
    ])

    return enu

def enu2ecef(enu, obs_lat, obs_long, obs_alt):
    """
    Convert local East, North, Up coordinates to ECEF coordinates given 
    a latitude, longitude and altitude

    Note: Must be geodetic coordinates and not geocentric, else the 
    elliptical nature of the earth is not accounted for
    """
    slat = np.sin(np.radians(obs_lat))
    slon = np.sin(np.radians(obs_long))
    clat = np.cos(np.radians(obs_lat))
    clon = np.cos(np.radians(obs_long))

    obs_ecef = lla2ecef(obs_lat, obs_long, obs_alt)

    ecef = np.matmul(np.array([
        [- slon, -slat * clon, clat * clon],
        [clon, -slat * slon, clat * slon],
        [0, clat, slat]
    ]), enu) + obs_ecef

    return ecef

def lla2ecef(lat, lon, alt):
    a = 6378137
    a_sq = a ** 2
    e = 8.181919084261345e-2
    e_sq = e ** 2
    b_sq = a_sq * (1 - e_sq)

    lat = lat * np.pi / 180
    lon = lon * np.pi / 180
    alt = alt

    N = a / np.sqrt(1 - e_sq * np.sin(lat) ** 2)
    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = ((b_sq / a_sq) * N + alt) * np.sin(lat)

    result = np.array([x, y, z])

    return result

def deg_to_dms(deg):
    """
    Converts decimal degrees to degrees, minutes, and seconds in sexagesimal format.

    Args:
        deg: Decimal degrees value.

    Returns:
        A tuple containing degrees (int), minutes (int), and seconds (float).
    """
    degrees = int(deg)
    minutes = int((deg - degrees) * 60)
    seconds = (deg - degrees - minutes/60) * 3600
    return degrees, minutes, seconds

def format_dms(deg, hemisphere):
    """
    Formats degrees, minutes, and seconds into a string with hemisphere indicator.

    Args:
        deg: Degrees value (float).
        hemisphere: Hemisphere indicator ("N" for north, "S" for south, 
                    "E" for east, or "W" for west).

    Returns:
        A formatted string in degrees, minutes, seconds, and hemisphere format.
    """
    degrees, minutes, seconds = deg_to_dms(deg) 
    return f"{abs(degrees)}°{abs(minutes):02}'{abs(seconds):.1f}\"{hemisphere}"

def lat_long_to_string(latitude, longitude):
    """
    Converts latitude and longitude from decimal degrees to a formatted string.

    Args:
        latitude: Decimal latitude value.
        longitude: Decimal longitude value.

    Returns:
        A formatted string with latitude and longitude in degrees, minutes, 
        seconds, and hemisphere format.
    """
    lat_string = format_dms(latitude, "N" if latitude > 0 else "S")
    lon_string = format_dms(longitude, "E" if longitude > 0 else "W")
    return f"{lat_string}+{lon_string}"

main()