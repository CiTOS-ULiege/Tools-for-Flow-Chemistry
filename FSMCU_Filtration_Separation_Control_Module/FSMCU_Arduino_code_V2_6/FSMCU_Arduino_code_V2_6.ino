#include <LiquidCrystal_I2C.h>  
#include <ADS1X15.h>  //library for ADC ADS1115
#include <Servo.h>    //library for servo motors
#include <EEPROM.h>

ADS1115 ADS_0(0x49); //standard address, pin ADDR to VCC
ADS1115 ADS_1(0x48); //standard address, pin ADDR to GND
ADS1115 ADS_2(0x4B); //standard address, pin ADDR to SCL
ADS1115 ADS_3(0x4A); //standard address, pin ADDR to SDA
LiquidCrystal_I2C lcd(0x27, 16, 2);

Servo servo_1;
Servo servo_2;
Servo servo_3;

const int bypass_valve_pin = 6, sep_valve_pin = 5, servo_valve_1_pin = 2, servo_valve_2_pin = 3, servo_valve_3_pin = 4;
const int servo_1_us_A = 650, servo_1_us_B = 1400, servo_2_us_A = 600, servo_2_us_B = 1350, servo_3_us_A = 2050, servo_3_us_B = 1300;
const unsigned long main_loop_intervall_1 = 400, servo_interval = 3000, bypass_interval = 20000, filer_change_interval = 10000;    //time intervall for the main loop Hall-sensor reading and for servo actuation 
const float pressure_threshold = 3.2; //threshold for pressure resulting in filter change
unsigned long main_loop_counter_1 = 0, bypass_counter = 0;                       //counter for Hall-sensor reading loop, counter for bypass time
unsigned long servo_1_counter = 0, servo_2_counter = 0, servo_3_counter = 0, filtration_counter = 0;  //used for servo actuation, allowing to give time for movement before detaching
bool servo_1_flag = 0, servo_2_flag = 0, servo_3_flag = 0, filter_change_flag = 0, pressure_control_mode = 0;// used for servo actuation, allowing to give time for movement before detaching
int servo_pos = 0, servo_no = 0, selection = 2, HallSensor1, HallSensor2, HallSensor3, HallSensor4;
byte servo_1_pos, previous_servo_1_pos, servo_2_pos, previous_servo_2_pos, servo_3_pos, previous_servo_3_pos, previous_sep_valve_value  = 0, sep_valve_value = 0, bypass_valve_value = 0, filtration_mode = 1, sep_mode = 1;
float pressure1 = 0;
String received_string = "";



void setup() {
  Serial.begin(115200); 
  lcd.begin(16,2);
  lcd.backlight();
  lcd.clear();
//ADC settings  (ADS_0 0-1: HS1; ADS_0 2-3: HS2; ADS_1 0-1: HS3; ADS_1 2-3: HS4; ADS_3 0-1: MPS1
      // HS1, HS2 - bottom line; HS3, HS4 - upper line
  ADS_0.setGain(8);
  ADS_0.setMode(1);
  ADS_0.setDataRate(0);
  ADS_0.begin();  //starts ADS0 analog digital converter  
  ADS_1.setGain(8);
  ADS_1.setMode(1);
  ADS_1.setDataRate(0);
  ADS_1.begin();  //starts ADS1 analog digital converter
  ADS_2.setGain(2);
  ADS_2.setMode(1);
  ADS_2.setDataRate(0);
  ADS_2.begin();  //starts ADS2 analog digital converter
  ADS_3.setGain(0);
  ADS_3.setMode(1);
  ADS_3.setDataRate(0);
  ADS_3.begin();  //starts ADS3 analog digital converter
//EEPROM reading
  servo_1_pos =  EEPROM.read(0);  //single byte store (0 or 1)
  servo_2_pos =  EEPROM.read(1);
  servo_3_pos =  EEPROM.read(2);
  filtration_mode = EEPROM.read(3);
  sep_mode = EEPROM.read(4);
  sep_valve_value = EEPROM.read(5);
  bypass_valve_value  = EEPROM.read(6);

}

void loop() {
  if ((millis() - main_loop_counter_1) >= main_loop_intervall_1) {    //main timed loop
    main_loop_counter_1 = millis();
    SerialCommunication();
    analogWrite(sep_valve_pin, sep_valve_value);
    analogWrite(bypass_valve_pin, bypass_valve_value);
    if (pressure_control_mode == 0){
      pressure1 = (ADS_3.readADC_Differential_0_1() * 0.00018751 * 12.5 -6.25);   //Readout of MPS1 (p-senosr) and caluclation of pressure
    } 

    HallSensors();  //Function which reads responses from Hall sensors and sets automatically the sep_valve if the sep_mode==1
    SerialDataSending(HallSensor1, HallSensor2, HallSensor3, HallSensor4, pressure1, sep_valve_value, bypass_valve_value, servo_1_pos, servo_2_pos, servo_3_pos, filtration_mode, sep_mode);
    //priniting to serial as: "HS1, HS2, HS3, HS4, p1, sep_valv, bp_valv"
    LcdDisplayFunction(sep_valve_value, bypass_valve_value, pressure1, sep_mode, filtration_mode, servo_1_pos, servo_2_pos, servo_3_pos);

    //automated servo valve position changing 
    if (filtration_mode == 1) {
      if ((pressure1 >= pressure_threshold) && (filter_change_flag == 0)){  // sensing for pressure increase in currently working filter and proceeding to filter change procedure
        filter_change_flag = 1;
        bypass_valve_value = 255;
        if (servo_1_pos == 1) {
          servo_1_pos = 0;
          servo_2_pos = 0;
        }
        else {
          servo_1_pos = 1;
          servo_2_pos = 1;;
        }
      }
      if (((millis() - filtration_counter) >= filer_change_interval) && (filter_change_flag == 1)){
          filtration_counter = millis();
          filter_change_flag = 0;          
      }
      if (((millis() - bypass_counter) >= bypass_interval) && (bypass_valve_value == 255)){
        bypass_counter = millis();
        bypass_valve_value = 0;
      }
    }
    //Serial.print(filter_change_flag);
    //Serial.print(", ");
    //Serial.print(filtration_counter);
    //Serial.print(", ");
    //Serial.println(bypass_counter);

// Servo postion changing if servo_x_pos was changed
    if ((servo_1_pos != previous_servo_1_pos) || (servo_1_flag == 1)){
      Servo_actuation(1, servo_1_pos); //servo number, servo position us
      previous_servo_1_pos = servo_1_pos;
    }
    if ((servo_2_pos != previous_servo_2_pos) || (servo_2_flag == 1)){
      Servo_actuation(2, servo_2_pos); //servo number, servo position us
      previous_servo_2_pos = servo_2_pos;
    }
    if ((servo_3_pos != previous_servo_3_pos) || (servo_3_flag == 1)){
      Servo_actuation(3, servo_3_pos); //servo number, servo position us
      previous_servo_3_pos = servo_3_pos;
    }    
  
  // EEPROM Saving
  Update_Eeprom_Function(servo_1_pos, servo_2_pos, servo_3_pos, filtration_mode, sep_mode, sep_valve_value, bypass_valve_value);   
  
  }
}

// FUNCTIONS Section (Arduino compiler allows to have them in the end of sketch, it automatically creates "function prototypes" allowing recognition of them by main program loop)
//Function which reads responses from Hall sensors and sets the sep_valve
void HallSensors(){       
  HallSensor1 = abs(ADS_0.readADC_Differential_0_1());   //absolut value from readout of Hall-sensor 1 (bottom line)
  HallSensor2 = abs(ADS_0.readADC_Differential_2_3());   //absolut value from readout of Hall-sensor 2 (bottom line)
  HallSensor3 = abs(ADS_1.readADC_Differential_0_1());   //absolut value from readout of Hall-sensor 3 (bottom line)
  HallSensor4 = abs(ADS_1.readADC_Differential_2_3());   //absolut value from readout of Hall-sensor 4 (bottom line)
    //below simple logic, requires manual startup
  if ((sep_mode == 1) && ((HallSensor3 > 1000) || (HallSensor4 > 1000))) {
    sep_valve_value = 255; //fully open
  }
  if ((sep_mode == 1) && ((HallSensor1 > 1000) || (HallSensor2 > 1000))) {
    sep_valve_value = 0; //fully closed
  }
}


// Sending acquired data through serial
void SerialDataSending(int v1, int v2, int v3, int v4, float v5, int v6, int v7, int v8, int v9, int v10, int v11, int v12){
  Serial.print(v1);
  Serial.print(", ");
  Serial.print(v2);
  Serial.print(", ");
  Serial.print(v3);
  Serial.print(", ");
  Serial.print(v4);
  Serial.print(", ");
  Serial.print(v5);
  Serial.print(", ");
  Serial.print(v6);
  Serial.print(", ");
  Serial.print(v7);
  Serial.print(", ");
  Serial.print(v8);
  Serial.print(", ");
  Serial.print(v9);
  Serial.print(", ");
  Serial.print(v10);  
  Serial.print(", ");
  Serial.print(v11);
  Serial.print(", ");
  Serial.println(v12);
}

//Communication through serial, changing mode etc
void SerialCommunication(){
    while (Serial.available() > 0) {
    received_string = Serial.readStringUntil('\n');         //read string from serial until '\n' character present
    selection = received_string.substring(0, 1).toInt();
    switch (selection) {
      case 1:    //MANUAL (serial) separator valve control
        Serial.println("Sep valve serial control");
        sep_mode = 0;
        if (received_string.substring(2, 3).toInt() == 1){
          sep_valve_value = 255;
        }
        else if (received_string.substring(2, 3).toInt() == 0) {
          sep_valve_value = 0;
        }
      break;
      case 2:    //AUTO embeded vavle control
        sep_mode = 1;
        Serial.println("AUTO sep valve control");       
      break;
      case 3:    //MANUAL (serial) bypass valvel control
        if (received_string.substring(2, 3).toInt() == 1){
          bypass_valve_value = 255;
        }
        else if (received_string.substring(2, 3).toInt() == 0) {
          bypass_valve_value = 0;
        }
      break;
      case 4: // MANUAL servo valves control (each one separately) 
        filtration_mode = 0;
        if (received_string.substring(2, 3).toInt() == 0) { //conditions for basick fool-proofing, only values "0" or "1" will work
          servo_1_pos = 0; //example "4 1 0 0" for servo 1 position B, servo 2 position A, servo 3 position A (servo positions A and B are set as constants
        }
        if (received_string.substring(2, 3).toInt() == 1) {
          servo_1_pos = 1;
        }
        if (received_string.substring(4, 5).toInt() == 0) {
          servo_2_pos = 0;
        }
        if (received_string.substring(4, 5).toInt() == 1) {
          servo_2_pos = 1;
        }
        if (received_string.substring(6, 7).toInt() == 0) {
          servo_3_pos = 0;
        }
        if (received_string.substring(6, 7).toInt() == 1) {
          servo_3_pos = 1;
        }
      break;
      case 5: // SEMI-AUTO servo valves control (both filter valves in tandem, washing valve separately)
        filtration_mode = 0;
        //FILTER 1 - write 5 0 x; FILTER 2 - write 5 1 x; 5 x 0 - washing walve pos 1; 5 x 1 - washing valve pos 2
        if (received_string.substring(2, 3).toInt() == 0){
          servo_1_pos = 0;
          servo_2_pos = 0;
        }
        if (received_string.substring(2, 3).toInt() == 1){
          servo_1_pos = 1;
          servo_2_pos = 1;
        }
        if (received_string.substring(4, 5).toInt() == 1) {
          servo_3_pos = 1;
        }
        if (received_string.substring(4, 5).toInt() == 0) {
          servo_3_pos = 0;
        }
      break;
      case 6: // AUTO filtration module - servo valves auto control (SV1, SV2 filter valves and SV3 washing valve)
        filtration_mode = 1;
      break;
        case 7: // pressure measurement (type "7 0") or manual pressure value introduction (type "7 1 xx" where xx is pressure in bar)
        if (received_string.substring(2, 3).toInt() == 0){
          pressure_control_mode = 0;
        }
        if (received_string.substring(2, 3).toInt() == 1) {
          pressure_control_mode = 1;       
          pressure1 = received_string.substring(4, 7).toInt();
        }
      break;
    }  
  }
}

// Printing on LCD display 2x16
void LcdDisplayFunction(int v1, int v2, float v3, int sep_state, int filtr_state, int S1, int S2, int S3){
  lcd.setCursor(0,0);                                     
  lcd.print("SV:            ");
  lcd.setCursor(3,0);                                     
  if  (v1 > 200) {
    lcd.print("1");
  }
  else if (v1 < 10) {
    lcd.print("0");
  }
  lcd.setCursor(10,0);                                     
  lcd.print("bar");
  lcd.setCursor(5,0);                                     
  lcd.print(v3);
  lcd.setCursor(0,1);                                     
  lcd.print("BV:     "); 
  lcd.setCursor(3,1);                                     
  if  (v2 > 200) {
    lcd.print("1");
  }
  else if (v2 < 10) {
    lcd.print("0");
  }lcd.setCursor(14,1);
  lcd.print("S");                                       
  lcd.print(sep_state); 
  lcd.setCursor(14,0);
  lcd.print("F");                                    
  lcd.print(filtr_state);

/*
  if (state == 0) {
    lcd.setCursor(10,1);                                     
    lcd.print("MAN.");
  }
  if (state == 1) {
    lcd.setCursor(10,1);                                     
    lcd.print("AUTO");
  }
*/
  lcd.setCursor(5,1);                                     
  lcd.print("serv.");
  lcd.setCursor(10,1);                                     
  lcd.print(S1);
  lcd.setCursor(11,1);                                     
  lcd.print(S2);
  lcd.setCursor(12,1);                                     
  lcd.print(S3);
}


//Servo operation
void Servo_actuation(int servo_no, int servo_pos){
 int servo_us;
 switch (servo_no) {
      case 1:
        if (servo_pos == 0){
          servo_us = servo_1_us_A;
        }
        else servo_us = servo_1_us_B;
        if (servo_1_flag == 0) {
          servo_1_counter = millis();
          servo_1.attach(servo_valve_1_pin);
          servo_1.writeMicroseconds(servo_us);  //change to servo_us after applying setpoints
          servo_1_flag = 1;
        }
        if ((servo_1_flag == 1) && ((millis() - servo_1_counter) >= servo_interval)){
          servo_1.detach();
          servo_1_flag = 0;
        }
      break;
      case 2:
        if (servo_pos == 0){
          servo_us = servo_2_us_A;
        }
        else servo_us = servo_2_us_B;
        if (servo_2_flag == 0) {
          servo_2_counter = millis();
          servo_2.attach(servo_valve_2_pin);
          servo_2.writeMicroseconds(servo_us);  //change to servo_us after applying setpoints
          servo_2_flag = 1;
        }
        if ((servo_2_flag == 1) && ((millis() - servo_2_counter) >= servo_interval)){
          servo_2.detach();
          servo_2_flag = 0;
        }
      break;
      case 3:
        if (servo_pos == 0){
          servo_us = servo_3_us_A;
        }
        else servo_us = servo_3_us_B;
        if (servo_3_flag == 0) {
          servo_3_counter = millis();
          servo_3.attach(servo_valve_3_pin);
          servo_3.writeMicroseconds(servo_us);  //change to servo_us after applying setpoints
          servo_3_flag = 1;
        }
        if ((servo_3_flag == 1) && ((millis() - servo_3_counter) >= servo_interval)){
          servo_3.detach();
          servo_3_flag = 0;
        }
      break;        
 }
}

//EEPROM updating
void Update_Eeprom_Function(byte byte1, byte byte2, byte byte3, byte byte4, byte byte5, byte byte6, byte byte7){
  EEPROM.update(0, byte1);
  EEPROM.update(1, byte2);
  EEPROM.update(2, byte3);
  EEPROM.update(3, byte4);
  EEPROM.update(4, byte5);
  EEPROM.update(5, byte6);
  EEPROM.update(6, byte7);
} 
