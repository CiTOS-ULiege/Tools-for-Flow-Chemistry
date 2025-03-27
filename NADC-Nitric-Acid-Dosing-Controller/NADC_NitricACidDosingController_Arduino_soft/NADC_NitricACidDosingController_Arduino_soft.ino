//        NADC V2.6
//        Nitric Acid Dosing Controller, version 2.6
//        Previously called FNCB, Furfural Nitration Control Box, version 2.5
//Program allowing mechanical control of 2 valves (using servomotors) and small DC (12 V) pump.
//Author: Hubert Hellwig, postdoctoral researcher at CiTOS, University of Liege, Belgium
//Date of V 2.6, 27/08/2024
// There is no major changes between V2.5 and V2.6

//INFO: ASCII string sent by PC should look like: "X YYYY" (servos); "3 Y"(pump) or "4" (status request)
//INFO: in the case of "1" and "2", it will control servo 1 and 2, while "YYYY" is the microsecond amount for
//INFO: positioning the servo: 550 is the lowest set, 0 degree, and 1166 is 90 degree, max is around 2500
//INFO: Example: "1 1166" will rotate servo1 to 90degree, when "2 550" will rotate servo2 to 0 degree
//INFO: in the case of "3", Y should be 0 or 1, what will switch the pump off or on
//INFO: in the case of "4" it will call for status, no additional characters required
//INFO: Status: "S1: YYYY; S2: YYYY; P: Y"

#include <LiquidCrystal_I2C.h>  
#include <Servo.h>
#include <EEPROM.h>

#define LED_PIN_1 5                   // set pin number 5 as LED 1
#define LED_PIN_2 4                   // set pin number 4 as LED 2
#define LED_PIN_3 3                   // set pin number 3 as LED 3
#define LED_PIN_4 2                   // set pin number 2 as LED 4
#define switch_pin_1 A0               // set pin number 0 as switch 1
#define switch_pin_2 A1               // set pin number 1 as switch 2
#define switch_pin_3 A2               // set pin number 1 as switch 3
#define pump_pin 6                    // set pin number 6 as a PWM output for peristaltic pump control 
LiquidCrystal_I2C lcd(0x27, 16, 2);            // Configure LiquidCrystal_I2C library with 0x27 address, 16 columns and 2 rows
Servo servo1;                                // create servo object to control a servo, twelve servo objects can be created on most boards
Servo servo2;                                // create servo object to control a servo, twelve servo objects can be created on most boards
//
const int servo_pos_histeresis = 50;            //hysteresis for microsecond servo position to assign state A or B if postion sent by serial will be not identical with A or B
const unsigned long time_intervall_1 = 500;     //time intervall for EEPROM updating and partail LCD clearing 
const unsigned long time_intervall_2 = 750;     //time intervall for servo position change
const unsigned long time_intervall_3 = 500;      //time intervall for pump control
const unsigned long debounce_intervall = 50;     //Time for "debouncing" switches
const int servo1_pos_A = 550;     // Position A of servo 1 to be set by switch1, ANGLE = 0 degree; in us: 550 + 6.85 * 0
const int servo1_pos_B = 1166;    // Position B of servo 1 to be set by switch1, ANGLE = 90 degree; in us: 550 + 6.85 * 90
const int servo2_pos_A = 550;     // Position A of servo 2 to be set by switch2, ANGLE = 0 degree; in us: 550 + 6.85 * 0
const int servo2_pos_B = 1166;    // Position B of servo 2 to be set by switch2, ANGLE = 90 degree; in us: 550 + 6.85 * 90
const int pump_ON_period = 2;       //Fraction of time for pump to be in ACTIVE state, while switched ON
const int pump_OFF_period = 4;      //Fraction of time for pump to be in BREAK state, while switched ON
const int pump_PWM_value = 210;         // PWM duty cycle for pump motor (0-255), to be send to MOSFER motor controler
bool servo1_state = 0;
bool servo2_state = 0;
bool servo1_flag = 0;
bool servo2_flag = 0;
bool switch1_state = LOW;
bool switch2_state = LOW;
bool switch3_state = LOW;
bool previous_switch1 = LOW;
bool previous_switch2 = LOW;
bool previous_switch3 = LOW;
bool LCD_flag = 0;
unsigned long counter1=0;
unsigned long counter_servo1=0;
unsigned long counter_servo2=0;
unsigned long counter3=0;
unsigned long counter4=0;
unsigned long last_debounce_time;
int servo1_pos_us, servo2_pos_us, servo_1_pos_us_highByte, servo_1_pos_us_lowByte, servo_2_pos_us_highByte;
int servo_2_pos_us_lowByte, pump_counter, selection;
bool pump_state, current_switch1, current_switch2, current_switch3, previous_servo1_state, previous_servo2_state;
bool led1_state, led2_state, led3_state, led4_state, servo1_serial_flag, servo2_serial_flag;
String received_string = "";
String status = "";


void setup() {
//Serial and LCD initialisation; setting pins functions
  Serial.begin(115200);   
  lcd.begin(16,2);
  lcd.backlight();
  lcd.clear();
  pinMode(switch_pin_1, INPUT);
  pinMode(switch_pin_2, INPUT);
  pinMode(switch_pin_3, INPUT);
  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT); 
//
//EEPROM reading, low byte and high byte are saved separately
  servo_1_pos_us_highByte = EEPROM.read(0);
  servo_1_pos_us_lowByte = EEPROM.read(1);
  servo_2_pos_us_highByte = EEPROM.read(2);
  servo_2_pos_us_lowByte = EEPROM.read(3);
  servo1_pos_us = word(servo_1_pos_us_highByte, servo_1_pos_us_lowByte);
  servo2_pos_us = word(servo_2_pos_us_highByte, servo_2_pos_us_lowByte);
  pump_state = EEPROM.read(4);
//
//Setting the servoX_state variables to allow function of switches immediately after restarting the device
  if (servo1_pos_us <= (servo1_pos_A + servo_pos_histeresis)) {  //change of servo status to allow opeartion of swich1 from the first switching
    servo1_state = 0;
  }
  if (servo1_pos_us >= (servo1_pos_B - servo_pos_histeresis)) {  //change of servo status to allow opeartion of swich1 from the first switching
    servo1_state = 1;
  }
  if (servo2_pos_us <= (servo2_pos_A + servo_pos_histeresis)) {  //change of servo status to allow opeartion of swich2 from the first switching
    servo2_state = 0;
  }
  if (servo2_pos_us >= (servo2_pos_B - servo_pos_histeresis)) {  //change of servo status to allow opeartion of swich2 from the first switching
    servo2_state = 1;
  }
  previous_servo1_state = servo1_state;
  previous_servo2_state = servo2_state;
//
}

void loop() {
//Serial comunication
  while (Serial.available() > 0) {
    received_string = Serial.readStringUntil('\n');         //read string from serial until '\n' character present
    Serial.println(received_string);                        //print readed string to confirm if received correctly
    selection = received_string.substring(0, 1).toInt();
    Serial.println(selection);
    switch (selection) {
      case 1:    //servo valve 1 case
        if ((received_string.substring(2, 6).toInt() > 500) && (received_string.substring(2, 6).toInt() < 2500)) {  // convert to integer (basic foolproofing...)
          servo1_pos_us = received_string.substring(2, 6).toInt();                   
          servo1_serial_flag = 1;
          Serial.println(servo1_pos_us);
        }  
      break;
      case 2:    //servo valve 2 case
        if ((received_string.substring(2, 6).toInt() > 500) && (received_string.substring(2, 6).toInt() < 2500)) {  // convert to integer (basic foolproofing...)
          servo2_pos_us = received_string.substring(2, 6).toInt();               
          servo2_serial_flag = 1;
          Serial.println(servo2_pos_us);     
        }
      break;
      case 3:     //pump 1 case
        if ((received_string.substring(2).toInt() == 0) || (received_string.substring(2).toInt() == 1)) {  // convert to integer (basic foolproofing...)
          pump_state = received_string.substring(2).toInt();                
        }
      break;
      case 4:    // status case
        status = "S1: " + String(servo1_pos_us) + "; S2: " + String(servo2_pos_us) + "; P: " + String(pump_state);     
        Serial.println(status);
      break;
    }  
  }
//  
// Switches reading
  current_switch1 = digitalRead(switch_pin_1);
  current_switch2 = digitalRead(switch_pin_2);
  current_switch3 = digitalRead(switch_pin_3);
//
// Debouncing switch1 (servo1 switch)
  if (current_switch1 != previous_switch1) {
    last_debounce_time = millis();
  }
  if ((millis() - last_debounce_time) > debounce_intervall) {  
    if (current_switch1 != switch1_state) {
      switch1_state = current_switch1;
      if (switch1_state == HIGH) {
        // Action to do when switch 1 pressed
        servo1_state = !servo1_state;      
      }
    }
  } 
// 
// Debouncing switch2 (servo2 switch)
  if (current_switch2 != previous_switch2) {
    last_debounce_time = millis();
  }  
  if ((millis() - last_debounce_time) > debounce_intervall) {  
    if (current_switch2 != switch2_state) {
      switch2_state = current_switch2;
      if (switch2_state == HIGH) {
        // Action to do when switch 2 pressed
        servo2_state = !servo2_state;    
      }
    }
  }
//
// Debouncing switch3  (pump switch)
  if (current_switch3 != previous_switch3) {
    last_debounce_time = millis();
  }  
  if ((millis() - last_debounce_time) > debounce_intervall) {  
    if (current_switch3 != switch3_state) {
      switch3_state = current_switch3;
      if (switch3_state == HIGH) {
        // Action to do when switch 2 pressed
        pump_state = !pump_state;      
      }
    }
  } 
//
//Servo 1
  if ((servo1_state != previous_servo1_state) || (servo1_serial_flag == 1)) {
    if (servo1_flag == 0) {
      counter_servo1 = millis();
    }
    servo1_flag = 1;
    if (servo1_serial_flag != 1) {
      if (servo1_state == 0) {
        servo1_pos_us = servo1_pos_A;
      }
      if (servo1_state == 1) {
        servo1_pos_us = servo1_pos_B;
      }
    }
    if ((servo1_pos_us <= (servo1_pos_A + servo_pos_histeresis)) && (servo1_serial_flag == 1)) {  //change of servo status to reversed value set by serial comm.
      servo1_state = 0;
    }
    if ((servo1_pos_us >= (servo1_pos_B - servo_pos_histeresis)) && (servo1_serial_flag == 1)) {  //change of servo status to reversed value set by serial control comm.
      servo1_state = 1;
    }
    previous_servo1_state = servo1_state;
    servo1.attach(10);
    servo1.writeMicroseconds(servo1_pos_us);  
  } 
  if ((servo1_flag == 1) && ((millis() - counter_servo1) >= time_intervall_2)) {
    servo1.detach();     
    servo1_flag = 0;
    servo1_serial_flag = 0;
  }
//
//Servo 2
  if ((servo2_state != previous_servo2_state) || (servo2_serial_flag == 1)) {
    if (servo2_flag == 0) {
      counter_servo2 = millis();
    }
    servo2_flag = 1;
    if (servo2_serial_flag != 1) {
      if (servo2_state == 0) {
        servo2_pos_us = servo2_pos_A;
      }
      if (servo2_state == 1) {
        servo2_pos_us = servo2_pos_B;
      }
    }
    if ((servo2_pos_us <= (servo2_pos_A + servo_pos_histeresis)) && (servo2_serial_flag == 1)) {  //change of servo status to reversed value set by serial comm.
      servo2_state = 0;
    }
    if ((servo2_pos_us >= (servo2_pos_B - servo_pos_histeresis)) && (servo2_serial_flag == 1)) {  //change of servo status to reversed value set by serial control comm.
      servo2_state = 1;
    }
    previous_servo2_state = servo2_state;
    servo2.attach(9);
    servo2.writeMicroseconds(servo2_pos_us);  
  } 
  if ((servo2_flag == 1) && ((millis() - counter_servo2) >= time_intervall_2)) {
    servo2.detach();     
    servo2_flag = 0;
    servo2_serial_flag = 0;
  }  
//
//Pump
  if (millis() - counter3 > time_intervall_2) {  
    counter3 = millis();
    if ((pump_state == 1) && (millis() - counter4 > time_intervall_3)) {
      counter4 = millis();
      pump_counter++;
      if (pump_counter <= pump_ON_period) {
        analogWrite(pump_pin, pump_PWM_value);
        lcd.setCursor(10,0);                                
        lcd.print("P:ACT");
      }
      if ((pump_counter > pump_ON_period) && (pump_counter <= (pump_ON_period+pump_OFF_period))) {
        analogWrite(pump_pin, 0);
        lcd.setCursor(10,0);                                
        lcd.print("P:BRK");
      }
      if (pump_counter > (pump_ON_period+pump_OFF_period)) {
        pump_counter = 0;
      }
    }
    if (pump_state == 0) {
      analogWrite(pump_pin, 0);
      lcd.setCursor(10,0);                                
      lcd.print("P:OFF");
    }
  }    
//
// LCD status display
  lcd.setCursor(0,0);                                
  lcd.print("S1:");       
  lcd.print(servo1_pos_us);
  lcd.setCursor(0,1);
  lcd.print("S2:");
  lcd.print(servo2_pos_us);   
//
//LED indication of servo1 and servo2 positions A or B
  if (servo1_pos_us <= (servo1_pos_A + servo_pos_histeresis)) {  //Led indication workin also if different angle will be send by serial comm.  
    led1_state = HIGH;
    led2_state = LOW;
  }
  if (servo1_pos_us >= (servo1_pos_B - servo_pos_histeresis)) {  //Led indication workin also if different angle will be send by serial comm.
    led1_state = LOW;
    led2_state = HIGH;
  }
  if (servo2_pos_us <= (servo2_pos_A + servo_pos_histeresis)) {  //Led indication working also if a different angle will be send by the serial comm.  
    led3_state = HIGH;
    led4_state = LOW;
  }
  if (servo2_pos_us >= (servo2_pos_B - servo_pos_histeresis)) {  //Led indication working also if a different angle will be send by the serial comm.
    led3_state = LOW;
    led4_state = HIGH;
  }
//LED indication of other positions of servo1 and servo2: if the servo position is between A nd B or above B, both LED will be illuminated
  if ((servo1_pos_us < (servo1_pos_B - servo_pos_histeresis)) && (servo1_pos_us > (servo1_pos_A + servo_pos_histeresis)) || (servo1_pos_us > (servo1_pos_B + servo_pos_histeresis))) { 
    led1_state = HIGH;
    led2_state = HIGH;
  }
  if ((servo2_pos_us < (servo2_pos_B - servo_pos_histeresis)) && (servo2_pos_us > (servo2_pos_A + servo_pos_histeresis)) || (servo2_pos_us > (servo2_pos_B + servo_pos_histeresis))) { 
    led3_state = HIGH;
    led4_state = HIGH;
  }  
//
// IF condition clearing parts of LCD and updating EEPROM each time_intervall
  if (millis() - counter1 >= time_intervall_1) {
    counter1 = millis();
    //LCD clearing servo positions display 
    lcd.setCursor(0,0);                                     
    lcd.print("       ");
    lcd.setCursor(0,1);                                
    lcd.print("       ");  
    //EEPROM updating, highByte and lowByte used to divide integer servo_pos_us to bytes (as 1 "cell" of EEPROM can be written up to 255)
    EEPROM.update(0, highByte(servo1_pos_us));
    EEPROM.update(1, lowByte(servo1_pos_us));    
    EEPROM.update(2, highByte(servo2_pos_us));
    EEPROM.update(3, lowByte(servo2_pos_us));
    EEPROM.update(4, pump_state); 
  }
//
//LED indication of servo1 and servo2 positions
  digitalWrite(LED_PIN_1, led1_state);
  digitalWrite(LED_PIN_2, led2_state);
  digitalWrite(LED_PIN_3, led3_state);
  digitalWrite(LED_PIN_4, led4_state);
//
//switches states for debouncing
  previous_switch1 = current_switch1;
  previous_switch2 = current_switch2;
  previous_switch3 = current_switch3;
}