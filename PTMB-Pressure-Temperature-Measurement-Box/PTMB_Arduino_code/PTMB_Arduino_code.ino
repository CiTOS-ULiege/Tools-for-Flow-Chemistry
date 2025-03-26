// PTMB - Pressure Temperature Measurement Box, V1
// Reading of pressure sensor (ADS1115, 0.5 - 4.5 V gives 0-50 bar)
// Reading of thermocouple (MCP9600, module from SeeedStuido)
// Displaying on LCD 2x16 (with I2C adapter)
// Sending data through serial communication to PC
// by Hubert Hellwig, CiTOS, University of Liege, Belgium, 09/JAN/2024
// The code is based on modified fragments from examples found in Internet

#include <LiquidCrystal_I2C.h>          // Include LiquidCrystal_I2C library 
#include <Wire.h>
#include <Adafruit_I2CDevice.h>         // libraries for I2C
#include <Adafruit_I2CRegister.h>
#include <ADS1X15.h>                    // library for ADS ADC
#include "Adafruit_MCP9600.h"
#define I2C_ADDRESS (0x60)              // address of MCP9600

Adafruit_MCP9600 mcp;                   // Address defined above
ADS1115 ADS_0(0x49);                    // ADC address set to 0x49 (BIN 1001001) (addr pin connected to VDD)
LiquidCrystal_I2C lcd(0x27, 16, 2);     // Configure LiquidCrystal_I2C library with 0x27 address, 16 columns and 2 rows

int16_t raw_0 = 0;            // variable for the raw ADC_0 A0 value
float d = 0.00018751;         // value to convert raw into voltage (6.144/32767)
float voltage_0 = 0;          // variable for calculated voltage value
float a = 12.5;               // a, b: variables for calculating pressure from voltage (linear equation)
float b = -6.25;              // 0.5 V gives 0 bar, 4.5 V gives 50 bar
float pressure = 0;           // variable for calculated pressure value

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  lcd.init();
  lcd.begin(16,2);
  lcd.backlight();
  if (! mcp.begin(I2C_ADDRESS)) {                   //Initialise the driver with I2C_ADDRESS and the default I2C bus.
    Serial.println("Temp sensor not found. Check wiring!");  //If not availavle display error on LCD
    while (1);
  }
  mcp.setADCresolution(MCP9600_ADCRESOLUTION_18);
  mcp.enable(true);
  ADS_0.setGain(0);
  ADS_0.setMode(1);
  ADS_0.setDataRate(0);
  ADS_0.begin();  //starts ADS analog digital converter
}

void loop() {
  raw_0 = ADS_0.readADC_Differential_0_1();   // read the value from ADS1115 ADC, differential: input A0 vs A1
  voltage_0 = raw_0 * d;                      // calculate the voltage from ADC value
  pressure = (voltage_0 * a + b);             // calculate the pressure from voltage value
  Serial.print("Thermocouple: ");
  Serial.print(mcp.readThermocouple());       // read and send the temperature value from thermocouple read by MCP9600
  Serial.print(" Ambient: ");
  Serial.print(mcp.readAmbient());            // read and send the ambient temperature of MCP9600
  Serial.print(" Pressure: ");
  Serial.print(pressure);                     // send current value of pressure
  Serial.print(" Raw: ");
  Serial.println(raw_0);                      // send raw_0 value
  lcd.clear();                                // clears LCD and positions cursor in upper left position
  lcd.print("p= ");  
  lcd.print(pressure);                        // display current pressure value
  lcd.print(" bar"); 
  lcd.setCursor(0,1);
  lcd.print("Temp= "); 
  lcd.print(mcp.readThermocouple());          // read and display current temperature from thermocouple
  lcd.print(" ");
  lcd.print((char)223);                       // 'degree' symbol
  lcd.print("C");
  delay(500);                                 // force the cycle time to around 2 per second (500 ms delay)
}
