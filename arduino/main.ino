#include <Wire.h>
#include <Adafruit_INA219.h>
#include <LiquidCrystal_I2C.h>

Adafruit_INA219 ina219;
LiquidCrystal_I2C lcd(0x27, 20, 4); // 20 colonnes, 4 lignes

float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0;
float loadvoltage = 0;
float power_mW = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialisation du capteur avec calibration optimisée pour faibles courants
  if (!ina219.begin()) {
    Serial.println("INA219 non detecte");
    while (1) { delay(10); }
  }
  
  // Configuration pour une meilleure précision avec les faibles courants
  // Choisissez l'une des options suivantes selon votre application:
  
  // Option 1: Pour courants jusqu'à 1A (précision pour faibles courants)
  ina219.setCalibration_32V_1A();
  
  // Option 2: Pour courants jusqu'à 320mA (plus précis pour très faibles courants)
  // ina219.setCalibration_32V_320mA();
  
  // Option 3: Pour courants jusqu'à 100mA (très haute précision pour micro-courants)
  // ina219.setCalibration_16V_100mA();
  
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("INA219 Calibre");
  lcd.setCursor(0, 1);
  lcd.print("Mode: 1A");
  delay(2000);
}

void loop() {
  // Lecture des données avec calibration
  shuntvoltage = ina219.getShuntVoltage_mV();
  busvoltage = ina219.getBusVoltage_V();
  current_mA = ina219.getCurrent_mA();
  power_mW = ina219.getPower_mW();
  loadvoltage = busvoltage + (shuntvoltage / 1000.0);
  
  lcd.clear();
  
  // Affichage détaillé pour le débogage
  lcd.setCursor(0, 0);
  lcd.print("U:");
  lcd.print(loadvoltage, 2);   // Tension de charge avec 2 décimales
  lcd.print("V I:");
  lcd.print(current_mA, 1);   // Courant avec 1 décimale
  
  lcd.setCursor(0, 1);
  lcd.print("P:");
  lcd.print(power_mW, 1);     // Puissance avec 1 décimale
  lcd.print("mW S:");
  lcd.print(shuntvoltage, 2); // Tension de shunt avec 2 décimales
  
  // Affichage des tensions pour diagnostic
  lcd.setCursor(0, 2);
  lcd.print("Bus:");
  lcd.print(busvoltage, 2);
  lcd.print("V");
  
  // Envoi des données complètes pour analyse
  Serial.print(loadvoltage, 3);
  Serial.print(",");
  Serial.print(current_mA, 3);
  Serial.print(",");
  Serial.print(power_mW, 3);
  Serial.print(",");
  Serial.print(busvoltage, 3);
  Serial.print(",");
  Serial.println(shuntvoltage, 3);
  
  delay(1000);  // Délai de 1 seconde entre les mesures
}