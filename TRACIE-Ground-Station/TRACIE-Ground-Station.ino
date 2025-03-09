#include <Arduino.h>
#include <RadioLib.h>
#include <SPI.h>

// ======= Direct Influx DB logging setup ====== 
// #include <WiFiMulti.h>
// WiFiMulti wifiMulti;
// #define DEVICE "ESP32"
// #if defined(ESP8266)
// #include <ESP8266WiFiMulti.h>
// ESP8266WiFiMulti wifiMulti;
// #define DEVICE "ESP8266"
// #endif
// #include <InfluxDbClient.h>
// #include <InfluxDbCloud.h>
// // WiFi AP SSID
// #define WIFI_SSID "Samspixel"
// // WiFi password
// #define WIFI_PASSWORD "rockets123"
// #define INFLUXDB_URL "http://webserver.tdanvers.com:8086"
// #define INFLUXDB_TOKEN "OPJOAsaG56tE2Q7cFlsGptEnBnc_RpvEgbKi84okMDtDat6Tyh9RaJoNJxyxO-Y9SZ0Ay7Optf4UjJHgBbn9vg=="
// #define INFLUXDB_ORG "3af71037e75de95a"
// #define INFLUXDB_BUCKET "tracie2"
// // Time zone info
// #define TZ_INFO "UTC1"
  // Declare InfluxDB client instance with preconfigured InfluxCloud certificate
// InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);
// // Declare Data point
// Point measurement("tracker");
// // WIFI stuff
// uint32_t wifi_timer = millis();
// AsyncWebSocket server;
// const int port = 80; // Websocket server port

// // Replace with your Telegraph access token and path
// const char* telegraph_token = "your_telegraph_token";
// const char* path = "your_telegraph_path";  // Path to your Telegraph bot


// Variable to store your data
// String websocketString;


// Radio defines
#define SXMISO GPIO_NUM_12
#define SXMOSI GPIO_NUM_13
#define SXSCK GPIO_NUM_14
#define SXCTS GPIO_NUM_15 // SPI CS pin
#define SXRST GPIO_NUM_16
#define SXBUSY GPIO_NUM_17
#define SXDIO GPIO_NUM_27

// define the spi bus
SPIClass sxSPI = SPIClass(HSPI);
SPISettings spiSettings(2000000, MSBFIRST, SPI_MODE0);

SX1280 radio = new Module(SXCTS,SXDIO,SXRST,SXBUSY, sxSPI, spiSettings);

// SET 1: 2405.0 MHz
// SET 2: 2410.0 MHz
#define CHANNEL1 2405.0
#define CHANNEL2 2410.0

#define RADIO_FREQUENCY 2405.0
#define RADIO_BANDWIDTH 406.25
#define RADIO_SPREADING_FACTOR 8
#define RADIO_CODING_RATE 6
#define RADIO_SYNC_WORD 0x34
#define RADIO_POWER 6 // -9 for UK use, +6 for US use
#define RADIO_PREAMBLE_LENGTH 8 // 8 symbols


#define BUZZER_PIN GPIO_NUM_4
#define RED_LED_PIN GPIO_NUM_2

// flag to indicate that a packet was received
volatile bool receivedFlag = false;
#define NUM_BYTES 15

// Amplifier
#define AMP_RX_EN GPIO_NUM_21
#define AMP_SD_EN GPIO_NUM_25 


void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);

  sx1280_setup();

  happy_startup_noise();
}

struct GPSData {  // turn into flash logging struct???
  float latitude;
  float longitude;
  float altitude;
  byte fix;
  byte siv;
  float rssi;
  float snr;
  int state;
};


// void uploadToInfluxDb(void * parameter) {

//     GPSData *data = (GPSData *)parameter;
//     // Clear fields for reusing the point. Tags will remain the same as set above.
//     measurement.clearFields();

//     // Store measured value into point
//     measurement.addField("latitude", data->latitude, 10);
//     measurement.addField("longitude", data->longitude, 10);
//     measurement.addField("altitude", data->altitude, 10);
//     measurement.addField("fix", data->fix);
//     measurement.addField("siv", data->siv);
//     measurement.addField("RSSI", data->rssi, 3);
//     measurement.addField("SNR", data->snr, 3);
//     measurement.addField("state", data->state);

//     // Print what are we exactly writing
//     Serial.print("Writing from core "); Serial.print(xPortGetCoreID()); Serial.print(": ");
//     Serial.println(measurement.toLineProtocol());
  
//     // Check WiFi connection and reconnect if needed
//     if (wifiMulti.run() != WL_CONNECTED) {
//       Serial.println("Wifi connection lost");
//     }
  
//     // Write point
//     if (!client.writePoint(measurement)) {
//       Serial.print("InfluxDB write failed: ");
//       Serial.println(client.getLastErrorMessage());
//     }
// } // if receivedFlag


void loop() {
  	// // Check for Serial Availability
	if (Serial.available()) {
		// read a line from serial
		String line = Serial.readStringUntil('/n');
		if (line == "CHANNEL1") {
			radio.setFrequency(CHANNEL1);
			delay(1000);
		}
		else if (line == "CHANNEL2") {
			radio.setFrequency(CHANNEL2);
			delay(1000);
		}		
	}
  if(receivedFlag) {
    // turn on the red LED
    digitalWrite(RED_LED_PIN, HIGH);
    // reset flag
    receivedFlag = false;

    // Receive bytes - Load into byte arrat
    byte byteArr[NUM_BYTES];
    int numBytes = radio.getPacketLength();
    int state = radio.readData(byteArr, numBytes);

    // Put radio back in recieve mode
    radio.startReceive();

    // convert byte array to data we need
    float latitude = (float) ((byteArr[0] << 24) | (byteArr[1] << 16) | (byteArr[2] << 8) | byteArr[3]) / 10000000;
    float longitude = (float) ((byteArr[4] << 24) | (byteArr[5] << 16) | (byteArr[6] << 8) | byteArr[7]) / 10000000;
    float altitude = (float) ((byteArr[8] << 24) | (byteArr[9] << 16) | (byteArr[10] << 8) | byteArr[11]) / 1000;
    byte siv_fix = byteArr[12]; byte fix = siv_fix >> 6; byte siv = siv_fix & 0b00111111; // 2 bits for fix, 6 bits for siv#
    uint32_t max_altitude_m = (byteArr[13] << 8) | byteArr[14];

    // print the parsed data
    String str = "[DATA]: " + String(latitude, 7) + "," + String(longitude, 7) + "," + String(altitude, 7) + "," + String(fix) + "," + String(siv) + "," + String(max_altitude_m);
    
    // Add on radio parameters and state
    float rssi = radio.getRSSI();
    float snr = radio.getSNR();
    float freq_error = radio.getFrequencyError();
    str += ", " + String(rssi, 3) + ", " + String(snr, 4) + ", " + String(freq_error, 3) + ", " + String(state);

    // Send data over serial
    Serial.println(str);  



    // Form a struct to pass to the InfluxDB task
    // GPSData data = {latitude, longitude, altitude, fix, siv, rssi, snr, state};
    // GPSData *dataPtr = (GPSData *)pvPortMalloc(sizeof(GPSData));
    // dataPtr->latitude = latitude;
    // dataPtr->longitude = longitude;
    // dataPtr->altitude = altitude;
    // dataPtr->fix = fix;
    // dataPtr->siv = siv;
    // dataPtr->rssi = rssi;
    // dataPtr->snr = snr;
    // dataPtr->state = state;
    // uploadToInfluxDb(dataPtr);
}
}

void sx1280_setup() {
		// AMP SETUP:
	pinMode(AMP_RX_EN, OUTPUT);
	pinMode(AMP_SD_EN, OUTPUT);

	digitalWrite(AMP_RX_EN, HIGH);
	digitalWrite(AMP_SD_EN, HIGH);




	// pinMode(PB12, OUTPUT);
	// digitalWrite(PB12, HIGH); // Pull NSS high to start with
	sxSPI.begin(); // Getting -705 error (timed out while waiting for complete SPI command.)
	// sxSPI.setClockDivider(0); // 8 MHz (half of the 16 MHz clock speed)
	// sxSPI.setDataMode(SPI_MODE0);
	// sxSPI.setBitOrder(MSBFIRST);

	Serial.print(F("[SX1280] Initializing ... "));

	int state = -1;
	while (state != RADIOLIB_ERR_NONE) {
  		int state = radio.begin(RADIO_FREQUENCY, RADIO_BANDWIDTH, RADIO_SPREADING_FACTOR, RADIO_CODING_RATE, RADIO_SYNC_WORD, RADIO_POWER, RADIO_PREAMBLE_LENGTH);
		if (state == RADIOLIB_ERR_NONE) {
			Serial.print(F("success! Status code: "));
			Serial.println(state);
			break;
		}
		else {
			Serial.print(F("init failed, code "));
			Serial.println(state);
			delay(500);
		}
		delay(100);
	}

  // set the function that will be called
  // when new packet is received
  radio.setPacketReceivedAction(setFlag);

  // start listening for LoRa packets
  Serial.print(F("[SX1280] Starting to listen ... "));
  state = radio.startReceive();
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println(F("success!"));
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    while (true);
  }
}

// void flash_setup() {
// 	// Initialize flash library and check its chip ID.
//   if (!flash.begin()) {
//     Serial.println("Error, failed to initialize flash chip!");
//     while (1) {
//       delay(1);
//     }
//   }
//   Serial.print("Flash chip JEDEC ID: 0x");
//   Serial.println(flash.getJEDECID(), HEX);
//   // First call begin to mount the filesystem.  Check that it returns true
//   // to make sure the filesystem was mounted.
//   if (!fatfs.begin(&flash)) {
//     Serial.println("Error, failed to mount newly formatted filesystem!");
//     Serial.println(
//         "Was the flash chip formatted with the fatfs_format example?");
//     while (1) {
//       delay(1);
//     }
//   }
//   Serial.println("Mounted filesystem!");
//   Serial.println("[FLASH] Setup Complete");
// }
// this function is called when a complete packet
// is received by the module
// IMPORTANT: this function MUST be 'void' type
//            and MUST NOT have any arguments!

#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
  // we got a packet, set the flag
  receivedFlag = true;
}


void happy_startup_noise() { 
  tone(BUZZER_PIN, 400, 100);
  delay(100);
  tone(BUZZER_PIN, 500, 100);
  delay(100);
  tone(BUZZER_PIN, 600, 100);
  delay(100);
  tone(BUZZER_PIN, 700, 300);
  delay(300);

}

// void wifi_setup() {
 // // Connect to wifi
  // WiFi.begin("Samspixel", "rockets123");
  // while ((WiFi.status() != WL_CONNECTED) && (millis() - wifi_timer < 30000)) {
  //   delay(100);
  //   Serial.println("Connecting to WiFi...");
  // }
  // if (WiFi.status() != WL_CONNECTED) {
  //   Serial.println("Failed to connect to WiFi");
  // }
  // else {
  //   Serial.print("Connected to the WiFi network. IP address: ");
  //   Serial.println(WiFi.localIP());
  // }
  // // Setup wifi
  // WiFi.mode(WIFI_STA);
  // wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);
  // Serial.print("Connecting to wifi");
  // while (wifiMulti.run() != WL_CONNECTED) {
  //   Serial.print(".");
  //   delay(100);
  // }
  //   // Accurate time is necessary for certificate validation and writing in batches
  // // We use the NTP servers in your area as provided by: https://www.pool.ntp.org/zone/
  // // Syncing progress and the time will be printed to Serial.
  // timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");

  // // Check server connection
  // if (client.validateConnection()) {
  //   Serial.print("Connected to InfluxDB: ");
  //   Serial.println(client.getServerUrl());
  // } else {
  //   Serial.print("InfluxDB connection failed: ");
  //   Serial.println(client.getLastErrorMessage());
  // }

    // Add tags to the data point
  // measurement.addTag("device", "TRACIE_GS");
// }