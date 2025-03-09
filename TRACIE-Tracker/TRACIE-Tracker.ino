/*
	Sunride TRACIE GPS tracker
*/

// ===== #includes =====
#include <Wire.h> //Needed for I2C to GNSS
#include <SPI.h>  //Needed for SPI to SX1280

#include <SparkFun_u-blox_GNSS_v3.h> //http://librarymanager/All#SparkFun_u-blox_GNSS_v3
#include <RadioLib.h>

#include <SdFat.h>
#include <Adafruit_SPIFlash.h>

// // ===== GPS setup =====
TwoWire gnssWire = TwoWire(PB9, PB8);
SFE_UBLOX_GNSS gnss; // SFE_UBLOX_GNSS uses I2C. For Serial or SPI, see Example2 and Example3

// ===== SX1280 Setup =====
SPIClass sxSPI = SPIClass(PB15, PB14, PB13, PB12); //MOSI, MISO, SCK, NSS
SPISettings spiSettings(2000000, MSBFIRST, SPI_MODE0);

// ===== Radio Setup ======
// NSS pin:   PB12
// DIO1 pin:  PA8
// NRST pin:  PC5
// BUSY pin:  PC4
SX1280 radio = new Module(PB12, PA8, PC5, PC4, sxSPI, spiSettings);
int transmissionState = RADIOLIB_ERR_NONE;
// flag to indicate that a packet was sent
volatile bool transmittedFlag = false;

// // ==== Flash Setup =====
// Adafruit_SPIFlash flash(&flashTransport); // SPIFlash object
// FatVolume fatfs; // file system object from SdFat


// ===== Definitions =====
#define GREEN_LED PA2
#define BUZZER_PIN PA10

#define AMP_TX_ENABLE_PIN PB10
#define AMP_RX_ENABLE_PIN PB11
#define AMP_TEMP_SENSOR_PIN PA1

// SET 1: 2405.0 MHz
// SET 2: 2410.0 MHz
#define CHANNEL1 2405.0
#define CHANNEL2 2410.0

#define RADIO_FREQUENCY 2405.0
#define RADIO_BANDWIDTH 406.25 // Has to be somewhat high because there's a decent frequency error between boards.
#define RADIO_SPREADING_FACTOR 8
#define RADIO_CODING_RATE 6
#define RADIO_SYNC_WORD 0x34
#define RADIO_POWER 6 // -9 for UK use, +6 for US use (amp will take it up to 30 dBm)
#define RADIO_PREAMBLE_LENGTH 8 // 8 symbols

#define NUM_BYTES 15
byte telemetry_packet[NUM_BYTES];
uint32_t beeper_timer = millis();
byte fix_type = 0;
uint16_t max_altitude_m = 0;

// Flash file name - Make this dynamic for each flight with an ID number? flight1, flight2 etc
// #define FILE_NAME "TRACIE_DATA.csv" 

struct flash_data_struct {
	byte flight_id;
	uint32_t unixtime;
	uint32_t latitude;
	uint32_t longitude;
	uint32_t altitude;
	byte siv;
	byte fix;	
};

void setup()
{
	LL_PWR_SMPS_Disable();  // CRITICAL for power draw issues - Disable the STM32WB55 power amp (for RF stuff)
	Serial.begin(115200);
	pinMode(GREEN_LED, OUTPUT);

	gnns_setup();
	sx1280_setup();

	happy_startup_noise();
}

void gnns_setup() {
	Serial.println(F("[GNSS] Initialising ... "));
	gnssWire.begin();

	//myGNSS.enableDebugging(); // Uncomment this line to enable helpful debug messages on Serial

	while (gnss.begin(gnssWire) == false) //Connect to the u-blox module using Wire port
	{
		Serial.println(F("u-blox GNSS not detected at default I2C address. Retrying..."));
		delay (1000);
	}
	// Set the GNSS to output PVT data only once per second
	gnss.setI2COutput(COM_TYPE_UBX); //Set the I2C port to output UBX only (turn off NMEA noise)
	gnss.setNavigationFrequency(4); // Set the PVT output to 20 times per second
	gnss.setDynamicModel(DYN_MODEL_AIRBORNE4g); 
	gnss.setAutoPVT(true); // Enable automatic PVT output
	gnss.saveConfigSelective(VAL_CFG_SUBSEC_IOPORT); //Optional: save (only) the communications port settings to flash and BBR
	Serial.println("[GNSS] Setup complete");
}

void sx1280_setup() {
	// AMP SETUP:
	pinMode(AMP_TX_ENABLE_PIN, OUTPUT);
	pinMode(AMP_RX_ENABLE_PIN, OUTPUT);
	pinMode(AMP_TEMP_SENSOR_PIN, INPUT);

	// Keep amp off until ready to transmit
	digitalWrite(AMP_TX_ENABLE_PIN, LOW);
	digitalWrite(AMP_RX_ENABLE_PIN, LOW);


	pinMode(PB12, OUTPUT);
	digitalWrite(PB12, HIGH); // Pull Radio NSS high to start with
	sxSPI.begin(); 

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
	}

	Serial.println("[SX1280] Setup Complete");
	// For Interrupt based transmit
	// radio.setPacketSentAction(setFlag);
		// start transmitting the first packet
	// Serial.print(F("[SX1280] Sending first packet ... "));

	// you can transmit C-string or Arduino string up to
	// 256 characters long
	// transmissionState = radio.startTransmit("Hello World!");
}

// void flash_setup() {
// 	flashTransport.setClockSpeed(2000000, 2000000); // 2 MHz clock speed
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

void loop()	
{
	// Loop consists of:
	// 1. Checking if there's new serial data from USB (for configuration)
	// 2. Checking if there's new I2C data from the GNSS
	// 3. TRANSMITTING that data over the radio

	if ((fix_type != 0) && (millis() - beeper_timer > 5000)) {
			tone(BUZZER_PIN, 1000, 50);
			delay(100);
			tone(BUZZER_PIN, 1500, 50);
			delay(100);
			tone(BUZZER_PIN, 2000, 200);
			beeper_timer = millis();
		}
		else if ((fix_type == 0) && (millis() - beeper_timer > 5000)) {
			noTone(BUZZER_PIN);
			tone(BUZZER_PIN, 1200, 50);
			delay(100);
			tone(BUZZER_PIN, 800, 50);
			delay(100);
			tone(BUZZER_PIN, 400, 200);
			beeper_timer = millis();
		}

	if (gnss.getPVT() == true)
	{	
		digitalToggle(GREEN_LED);

  		int32_t raw_latitute = gnss.getLatitude(); // Degrees * 10^-7
		int32_t raw_longitude = gnss.getLongitude(); // Degrees * 10^-7
		int32_t raw_altitude = gnss.getAltitude(); // mm
		int32_t altitude_m = raw_altitude / 1000; // Meters

		byte siv = (gnss.getSIV() & 0xFF); // Number of satellites used in position solution
		fix_type = gnss.getFixType(); // 0: no fix, 1: dead reckoning, 2: 2D fix, 3: 3D fix, 4: GNSS + dead reckoning, 5: time only fix
		siv = siv & 0b00111111; fix_type = fix_type & 0b00000011;
		byte siv_fix = fix_type << 6 | siv; // The first 2 bits are the fix type, the last 6 bits are the SIV

		if (fix_type == 3) {
			if (altitude_m > max_altitude_m) {
				max_altitude_m = altitude_m;
			}
		}

		int32_t year = gnss.getYear();
		int32_t month = gnss.getMonth();
		int32_t day = gnss.getDay();
		int32_t hour = gnss.getHour();
		int32_t minute = gnss.getMinute();
		int32_t second = gnss.getSecond();

		// Get the current time from the GNSS module in unix time format
		uint32_t unix_time = gnss.getUnixEpoch();

		// float horizontal_accuracy = (float)gnss.getHorizontalAccuracy() / 1000.0f; // Meters
		// float vertical_accuracy = (float)gnss.getVerticalAccuracy() / 1000.0f; // Meters		

		// float latitude = raw_latitute / 10000000.0f; //Degrees
		// float longitude = raw_longitude / 10000000.0f; //Degrees
		// float altitude = raw_altitude / 1000.0f; // Meters

		// telemetry_packet_str = "Lat: " + String(latitude, 7) + " Lon: " + String(longitude, 7) + " Alt: " + String(altitude, 2) + "(m) SIV: " + String(siv) + " Fix: " + String(fix_type) + " HAcc: " + 
		// "Time: " + String(hour) + ":" + String(minute) + ":" + String(second);
		// Serial.println(telemetry_packet_str);
		

		// Form the telemetry packet
		telemetry_packet[0] = (raw_latitute >> 24) & 0xFF; telemetry_packet[1] = (raw_latitute >> 16) & 0xFF; telemetry_packet[2] = (raw_latitute >> 8) & 0xFF; telemetry_packet[3] = raw_latitute & 0xFF;
		telemetry_packet[4] = (raw_longitude >> 24) & 0xFF; telemetry_packet[5] = (raw_longitude >> 16) & 0xFF; telemetry_packet[6] = (raw_longitude >> 8) & 0xFF; telemetry_packet[7] = raw_longitude & 0xFF;
		telemetry_packet[8] = (raw_altitude >> 24) & 0xFF; telemetry_packet[9] = (raw_altitude >> 16) & 0xFF; telemetry_packet[10] = (raw_altitude >> 8) & 0xFF; telemetry_packet[11] = raw_altitude & 0xFF;
		telemetry_packet[12] = siv_fix;
		telemetry_packet[13] = (max_altitude_m >> 8) & 0xFF; telemetry_packet[14] = max_altitude_m & 0xFF;
		// telemetry_packet[13] = (unix_time >> 24) & 0xFF; telemetry_packet[14] = (unix_time >> 16) & 0xFF; telemetry_packet[15] = (unix_time >> 8) & 0xFF; telemetry_packet[16] = unix_time & 0xFF;
		
		Serial.print("Packet: ");
		for (int i = 0; i < NUM_BYTES; i++) {
			Serial.print(telemetry_packet[i], HEX);
			Serial.print(" ");
		}
		Serial.println();
		transmit_packet_blocking();
	}
}

// this function is called when a complete packet
// is transmitted by the module
// IMPORTANT: this function MUST be 'void' type
//            and MUST NOT have any arguments!
#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
  // we sent a packet, set the flag
  transmittedFlag = true;
  // turn off the AMP HERE when transmitting with interrupt?? 
}

void transmit_packet_blocking() {
	// turn on the amp
	digitalWrite(AMP_TX_ENABLE_PIN, HIGH);
	delay(30);
	Serial.print(F("[SX1280] Sending packet ... "));
	transmissionState = radio.transmit(telemetry_packet, NUM_BYTES);
	Serial.println("Transmission successful! State: " + String(transmissionState));


	if (transmissionState == RADIOLIB_ERR_NONE) {
	// the packet was successfully transmitted
		Serial.println(F("success!"));

	} else if (transmissionState == RADIOLIB_ERR_PACKET_TOO_LONG) {
	// the supplied packet was longer than 256 bytes
		Serial.println(F("too long!"));

	} else {
	// some other error occurred
		Serial.print(F("failed, code "));
		Serial.println(transmissionState);
	}
		// turn off the amp
	digitalWrite(AMP_TX_ENABLE_PIN, LOW);
	
}

void transmit_packet_interrupt() {
	if(transmittedFlag) {
		// reset flag
		transmittedFlag = false;
		if (transmissionState == RADIOLIB_ERR_NONE) {
			// packet was successfully sent
			Serial.println(F("transmission finished!"));

			} else {
			Serial.print(F("failed, code "));
			Serial.println(transmissionState);

		}

		// clean up after transmission is finished
		// this will ensure transmitter is disabled,
		// RF switch is powered down etc.
		radio.finishTransmit();
		// wait a second before transmitting again
				// turn on the amp
		digitalWrite(AMP_TX_ENABLE_PIN, HIGH);

		// send another one
		Serial.print(F("[SX1280] Sending another packet ... "));

		// transmissionState = radio.startTransmit(str);
		// you can also transmit byte array up to 256 bytes long
		transmissionState = radio.startTransmit(telemetry_packet, NUM_BYTES);
		delay(50);
		
		// turn off the amp
		// digitalWrite(AMP_TX_ENABLE_PIN, LOW);
	}
}

// void log_to_flash(flash_data_struct data) {
// 	// Take in custom data struct
// 	// Open the data file we are writing to  // TODO: Make this dynamic so that we have a unique file for every flight.
// 	File32 dataFile = fatfs.open(FILE_NAME, FILE_WRITE); 
// 	if (dataFile) {  
// 		// This method takes up a lot more bytes than just raw binary logging. 	
// 		// Maybe `flash.writeBuffer(addr, bufwrite, sizeof(bufwrite));` is  a more compact way? but then you have to manage your own file system /:(
// 		// Write to flash
// 		dataFile.print(data.flight_id); dataFile.print(",");
// 		dataFile.print(data.unixtime); dataFile.print(",");
// 		dataFile.print(data.latitude); dataFile.print(",");
// 		dataFile.print(data.longitude); dataFile.print(",");
// 		dataFile.print(data.altitude); dataFile.print(",");
// 		dataFile.print(data.siv); dataFile.print(",");
// 		dataFile.print(data.fix);
// 		dataFile.println();
// 		dataFile.close(); // Close the file again
// 		Serial.println("Wrote new measurement to data file!");
// 	}
// }

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