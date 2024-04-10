import time
import board
import adafruit_bmp3xx

i2c = board.I2C()
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
  
# While loop 
while True: 
    print("Pressure: {:6.1f}".format(bmp.pressure))
    print("Temperature: {:5.2f}".format(bmp.temperature))
    print("Altitude: {:5.2f}".format(bmp.altitude))
