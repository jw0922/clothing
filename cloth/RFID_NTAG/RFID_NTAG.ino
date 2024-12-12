#include <SPI.h>
#include <MFRC522.h>

// Define RFID module pins
#define RST_PIN 9  // Reset pin for MFRC522
#define SS_PIN 10  // Slave Select pin for MFRC522
MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create an instance of the MFRC522 class

void setup() {
  Serial.begin(9600); // Initialize serial communication at 9600 baud
  SPI.begin();        // Initialize SPI communication
  mfrc522.PCD_Init(); // Initialize the MFRC522 RFID module
}

void loop() {
  // Check if a new RFID card is present and readable
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String tag_id = "";  // String to store the tag ID
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      tag_id += String(mfrc522.uid.uidByte[i], HEX); // Convert each byte of the UID to hexadecimal and append to the tag ID
    }
    Serial.println(tag_id); // Print the tag ID to the serial monitor
    delay(1000); // Add a delay to prevent continuous reading of the same card
  }
}
