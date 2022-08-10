# For circuitpython only (for the moment)
# This script is tested on a WeAct BlackPill(F411) with external flash.
# For other boards please change your pin definition

from busio import SPI
from digitalio import DigitalInOut, Direction
from adafruit_bus_device.spi_device import SPIDevice

import board
import gu7000
import time

MOSI = board.B15
MISO = board.B14
SCK = board.B13

# reset pin
# Active Low, write 1 to it
reset = DigitalInOut(board.B1)
reset.direction = Direction.OUTPUT
reset.value = 1

# busy pin
# active high
# read only
busy = DigitalInOut(board.B0)  # readonly
busy.direction = Direction.INPUT

def routine():
	spi_interface = SPI(SCK, MOSI=MOSI)
	with spi_interface as spi_bus:
		cs = DigitalInOut(board.LED)  # optional, just because CPY need a CS pin
		device = SPIDevice(spi_bus, cs)
		with device as spi:
			spi.configure(baudrate=115200, polarity=0, phase=0, bits=8)  # according to the arduino lib
			ser = gu7000.SerialInterface(spi, reset_pin=reset, busy_pin=busy)
			display = gu7000.GU7000Display(144, 32, interface=ser)
			display.init()
			for i in range(3):
				display.vfd_print(b'Hello world! ')
				time.sleep(1)
				display.carriage_return()
				display.line_feed()
				display.vfd_print(i+48)
				display.vfd_print(b' ')
				for i in range(3):
					display.vfd_print(0x66)
				time.sleep(1)
			
			# display.clear()  # at your wish, it'll also set the cursor to 0,0
			display.set_cursor(0,0)

			# read from file to avoid stack exhaustion
			with open('bitmap.png.bin', 'rb') as f:
				display.draw_image(file_obj=f)
			
			time.sleep(1)
			display.blink(1, 1, 10, 10, 3)  # possibly won't work

routine()
