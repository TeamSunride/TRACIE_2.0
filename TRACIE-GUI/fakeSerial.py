import random
import time
import json
import sys
import io

# ---- FAKE SERIAL -----                    # Used to test interactions/features without real hardware
class FakeSerial:
    def __init__(self):
        self.open = True

    def isOpen(self):
        return self.open
    
    def readline(self):
        latitude = 55.433123             # Plotting a horizontal line at  MACH-X
        longitude = round(random.uniform(-5.691, -5.697), 6)  
        
        #======== Other options ============
        #latitude = 35.351439637257265                               # Plot horizontal line at Mojave
        #longitude = #round(random.uniform(-117.80,-117.85),6)
        
        altitude = round(random.uniform(100, 120), 2)
        fix = "10"
        #fix = str(random.randint(0, 1)) 
        siv = "10"
        max_altitude_m = altitude
        rssi = "10"
        snr = "10"
        freqerr = "1"
        radio_state = "0"                                     # radio_state = "0" for healthy packets only 
        #radio_state = str(random.randint(0, 1))              #To simulate randomised good/corrupted packets sent

        original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            fake_data = f"[DATA]:{latitude},{longitude},{altitude},{fix},{siv},{max_altitude_m},{rssi},{snr},{freqerr},{radio_state}\n"
            time.sleep(0.2)                                #Adjust send rate (seconds)
            print(json.dumps(fake_data), flush=True)        # Send data is sent to stdout as "[DATA]: 'lat', 'lon', 'alt'm'radio_state""    
            return fake_data.encode("utf-8")                # Simulate serial output as bytes
        finally:
            sys.stdout = original_stdout        # Restore stdout

# Exact format as data received from tracker's serial.
# Works identically for TRACIE_GUI.py's readSerial function