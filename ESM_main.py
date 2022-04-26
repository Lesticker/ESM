import RPi.GPIO as GPIO
import time
import serial
import sys
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import math
import itertools
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0
p = '/dev/ttyUSB0'
font = ImageFont.truetype('Times New Roman 400.ttf', 40)
data = []
counter = itertools.count()
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(
    SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
disp.clear((0, 0, 0))
disp.begin()

draw = disp.draw()
image = Image.open('maschek.png')
disp.display(image)
time.sleep(1.5)
disp.clear((0, 0, 0))



def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    rotated = textimage.rotate(angle, expand=1)
    image.paste(rotated, position, rotated)
      
        
def reading_serial_data_21bytes():
    data.clear()
    disp.clear()
    import ESM1200


def reading_serial_data_25bytes():
    data.clear()
    disp.clear()
    for x in range(0, 25):
        st = ser.read()
        data.append(ord(st))

    sum_of_bytes = sum(data) - data[24]
    check_sum = sum_of_bytes % 128

    if check_sum == data[24]:
        ESM_25bytes_decryption()
        

def ESM_25bytes_decryption():
    print(data)
    rangeEz = (data[3] >> 5)+((data[21] & 0b100000) >> 3)
    Ez = (((data[3] & 0b11111) << 7)+data[4])*pow(10, rangeEz-2)

    rangeEy = (data[5] >> 5)+((data[21] & 0b10000) >> 2)
    Ey = (((data[5] & 0b11111) << 7)+data[6])*pow(10, rangeEy-2)

    rangeEx = (data[7] >> 5)+((data[21] & 0b1000) >> 1)
    Ex = (((data[7] & 0b11111) << 7)+data[8])*pow(10, rangeEx-2)
    decrypted_value_of_E = round(math.sqrt(pow(Ex, 2) + pow(Ey, 2) + pow(Ez, 2)), 2)

    rangeHz = (((data[9] ) >> 5)+(data[21] & 0b100))
    Hz = (((data[9] & 0b11111) << 7)+data[10])*pow(10, rangeHz -1)

    rangeHy = ((data[11] ) >> 5)+((data[21] & 0b10) << 1)
    Hy = (((data[11] & 0b11111) << 7)+data[12])*pow(10, rangeHy -1)

    rangeHx = ((data[13] )>> 5)+((data[21] & 0b1) << 2)
    Hx = (((data[13] & 0b11111) << 7)+data[14])*pow(10, rangeHx -1)
    decrypted_value_of_H = round(
        math.sqrt(pow(Hx, 2) + pow(Hy, 2) + pow(Hz, 2)), 2)

    if decrypted_value_of_H < 1000:
        print(decrypted_value_of_H, ' nT')
        draw_rotated_text(disp.buffer, str(decrypted_value_of_H) +
                          '\n nT', (10, 40), 0, font, fill=(0, 255, 0))
    elif 1000 <= decrypted_value_of_H < 1000000:
        print(decrypted_value_of_H/1000.0, ' uT')
        draw_rotated_text(disp.buffer, str(
            decrypted_value_of_H/1000.0)+'\n uT', (10, 40), 0, font, fill=(255, 255, 0))
    elif 1000000 <= decrypted_value_of_H < 1000000000:
        print(decrypted_value_of_H/1000000.0, ' mT')
        draw_rotated_text(disp.buffer, str(
            decrypted_value_of_H/1000000.0)+'\n mT', (10, 40), 0, font, fill=(255, 0, 0))

    if decrypted_value_of_E < 1000:
        print(decrypted_value_of_E, 'V/m')
        draw_rotated_text(disp.buffer, str(decrypted_value_of_E) +
                          '\n V/m', (10, 200), 0, font, fill=(0, 255, 0))
    elif 1000 <= decrypted_value_of_E < 1000000:
        print(decrypted_value_of_E/1000.00, 'kV/m')
        draw_rotated_text(disp.buffer, str(
            decrypted_value_of_E/1000.0)+'\n kV/m', (10, 200), 0, font, fill=(255, 255, 0))
    elif 1000000 <= decrypted_value_of_E < 1000000000:
        print(decrypted_value_of_E/1000000.0, 'MV/m')
        draw_rotated_text(disp.buffer, str(
            decrypted_value_of_E/1000000.0)+'\n MV/m', (10, 200), 0, font, fill=(255, 0, 0))
    draw.line((0,160,240,160), fill=(255,255,255))
    disp.display()


while True:
    try:
        ser = serial.Serial(port=p, baudrate=38400, bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        for x in range(0, 25):
            st = ser.read()
            data.append(ord(st))
        if sum(data) == 0:
            ser.baudrate = 1200
            data.clear()
            for num in counter:
                reading_serial_data_21bytes()
        else:
            data.clear()
            for num in counter:
                reading_serial_data_25bytes()
    except Exception as error:
        ser.close()
        print('waiting for connection')
            
    time.sleep(1)


