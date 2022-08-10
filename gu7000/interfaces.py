from time import sleep
from .shared import Pin, reverse_byte


class GU7000Interface:
	# a basic prototype
	def init(self):
		# init the display
		pass

	def write(self, data):
		# write raw command(bytes) to the display
		pass

	def hard_reset(self):
		pass


class SerialInterface(GU7000Interface):

	def __init__(self, serial_object, reset_pin=None, busy_pin=None):
		self._serial = serial_object
		self._reset_pin = Pin(reset_pin, Pin.OUT) if reset_pin is not None else None
		self._busy_pin = Pin(busy_pin, Pin.IN, Pin.PULL_DOWN) if busy_pin is not None else None

	def _busy(self):
		if self._busy_pin is not None:
			return True if self._busy_pin.value() else False
		return False

	def init(self):
		self.hard_reset()

	def write(self, data):
		if isinstance(data, (bytes, bytearray)):
			for i in data:
				self._write_one_byte(i)
		elif isinstance(data, int):
			self._write_one_byte(data)
		else:
			print('Unsupported data type %s' % type(data))

	def _write_one_byte(self, number):
		_singlebuffer = bytearray(1)
		# VFD is LSB first
		# but cpy defaults to MSB first and don't have a way to change it
		_singlebuffer[0] = reverse_byte(number)
		while self._busy():
			pass
		self._serial.write(_singlebuffer)

	def hard_reset(self):
		if self._reset_pin is not None:
			# GU7000 reset pin active low
			self._reset_pin.value(0)
			sleep(1)
			self._reset_pin.value(1)


# vim: ts=4 noexpandtab
