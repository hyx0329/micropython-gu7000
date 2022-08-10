import serial

from gu7000 import SerialInterface, GU7000Display

ser = serial.Serial('/dev/ttyBmpTarg', baudrate=38400, bytesize=8, stopbits=1)

si = SerialInterface(ser)

dis = GU7000Display(144, 32, interface=si)

dis.vfd_print(b'Hello world')
dis.clear()
dis.cursor_on()
dis.blink()

import convert
im, width, height = convert.convert('./bitmap.png')

dis.draw_image(width, height, data=im)

