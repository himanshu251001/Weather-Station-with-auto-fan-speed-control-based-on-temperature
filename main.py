from machine import Pin, I2C
from machine import Pin, PWM
from time import sleep
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from bmp280 import *
import utime
import time
import network
import BlynkLib




# Initialize I2C and LCD
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.move_to(0,0)
lcd.putstr(" Weather Station")
lcd.move_to(0,1)
lcd.putstr("Raspberry PiPico ")
sleep(5)

# Calibration error in pressure (optional, set to 0 if not needed)
ERROR = -3  # hPa

# Create a BMP280 object
bmp280 = BMP280(i2c, addr=0x76, use_case=BMP280_CASE_WEATHER)

# Configure BMP280 settings
bmp280.power_mode = BMP280_POWER_NORMAL
bmp280.oversample = BMP280_OS_HIGH
bmp280.temp_os = BMP280_TEMP_OS_8
bmp280.press_os = BMP280_TEMP_OS_4
bmp280.standby = BMP280_STANDBY_250
bmp280.iir = BMP280_IIR_FILTER_2

print("BMP280 Object created successfully!\n")
WIFI_SSID = 'HM'
WIFI_PASS = 'password123'
BLYNK_AUTH = 'INw8-J5foj3V5CDyJfacj5ZRSfVAN5-k'

# Action as Wifi Station Mode (Client) 
wifi = network.WLAN(network.STA_IF)
if not wifi.isconnected():
    print("Connecting to WiFi...")
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASS)
    while not wifi.isconnected():
        print(".", end="_")
        time.sleep(1)

print('\nWifi connected, IP:', wifi.ifconfig()[0])
#
# Initialize Blynk Client and BlynkTimer
# blynk = BlynkLib.Blynk(BLYNK_AUTH)
blynk = BlynkLib.Blynk(BLYNK_AUTH)





########################################################

def motorMove(speed,direction,speedGP,cwGP,acwGP):
  if speed > 100: speed=100
  if speed < 0: speed=0
  Speed = PWM(Pin(speedGP))
  Speed.freq(50)
  cw = Pin(cwGP, Pin.OUT)
  acw = Pin(acwGP, Pin.OUT)
  Speed.duty_u16(int(speed/100*65536))
  if direction < 0:
      cw.value(0)
      acw.value(1)
  if direction == 0:
      cw.value(0)
      acw.value(0)
  if direction > 0:
      cw.value(1)
      acw.value(0)

# Function for calculating altitude from pressure and temperature values
def altitude_HYP(hPa, temperature):
    sea_level_pressure = 1013.25  # hPa
    pressure_ratio = sea_level_pressure / hPa
    altitude = (((pressure_ratio ** (1 / 5.257)) - 1) * temperature) / 0.0065
    return altitude

# Function for calculating altitude from international barometric formula
def altitude_IBF(pressure):
    sea_level_pressure = 1013.25  # hPa
    pressure_ratio = pressure / sea_level_pressure
    altitude = 44330 * (1 - (pressure_ratio ** (1 / 5.255)))
    return altitude

pwmPIN=16
cwPin=14 
acwPin=15
while True:
    # Acquire temperature value in Celsius
    blynk = BlynkLib.Blynk(BLYNK_AUTH)
    temperature_c = bmp280.temperature
    
    # Convert Celsius to Kelvin
    temperature_k = temperature_c + 273.15
    
    # Acquire pressure value in Pascal
    pressure = bmp280.pressure
    
    # Convert Pascal to hectopascal (hPa)
    pressure_hPa = (pressure * 0.01) + ERROR
    
    # Acquire altitude values from different formulas
    h = altitude_HYP(pressure_hPa, temperature_k)
    altitude_ibf = altitude_IBF(pressure_hPa)
    # Display sensor readings
    print("Temperature: {:.2f} °C".format(temperature_c))
    print("Pressure: {:.2f} hPa".format(pressure_hPa))
    print("Altitude (Hypsometric Formula): {:.2f} meters".format(h))
    print("Altitude (International Barometric Formula): {:.2f} meters".format(altitude_ibf))
    print("\n")
    
    
    blynk.virtual_write(0,temperature_c)  
    blynk.virtual_write(1,pressure_hPa)
    blynk.virtual_write(2,altitude_ibf)
    
    blynk.run()
    
    if(temperature_c >30):
        motorMove(100,1,pwmPIN,cwPin,acwPin)
    elif(temperature_c >28.5):
        motorMove(75,1,pwmPIN,cwPin,acwPin)
    elif(temperature_c >25):
        motorMove(60,1,pwmPIN,cwPin,acwPin)
    elif(temperature_c >22.5):
        motorMove(37.5,1,pwmPIN,cwPin,acwPin)
    elif(temperature_c >17):
        motorMove(25,1,pwmPIN,cwPin,acwPin)
    elif(temperature_c >12.5):
        motorMove(12.5,1,pwmPIN,cwPin,acwPin)
    else:
        motorMove(0,1,pwmPIN,cwPin,acwPin)
    sleep(5)
    
    
    
    lcd.clear()
    # Update LCD display
    lcd.move_to(0,0)
    lcd.putstr(" Weather Station")
    lcd.move_to(0,1)
    lcd.putstr("Raspberry PiPico ")
    sleep(5)

    lcd.move_to(0,0)
    lcd.putstr(" Pico Weather Stn ")
    lcd.move_to(0, 1)
    lcd.putstr(" Temp: {:.1f} C ".format(temperature_c))
    sleep(5)
    lcd.move_to(0,0)
    lcd.putstr(" Pico Weather Stn")
    lcd.move_to(0, 1)
    lcd.putstr("Press: {:.1f}hPa ".format(pressure_hPa))
    sleep(5)
    lcd.move_to(0,0)
    lcd.putstr(" Pico Weather Stn")
    lcd.move_to(0, 1)
    lcd.putstr(" Alt: {:.1f} mtr  ".format(altitude_ibf))
    sleep(5)
    lcd.clear()
    





