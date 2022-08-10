
import sys

implementation = sys.implementation.name  # it's a named tuple

if 'micropython' == implementation:
	try:
		from machine import Pin
	except ModuleNotFoundError:
		Pin = lambda *args: None
elif 'circuitpython' == implementation:
	# need to mangle a bit
	# This is a workaround, cpy and mpy are fundamentally different
	class Pin:
		OUT = 1
		IN = 0
		PULL_UP = 1
		PULL_DOWN = 0

		def __init__(self, pin, *args, **kwargs):
			self._pin = pin
		
		def value(self, value=None):
			if isinstance(value, (bool, int)):
				self._pin.value = value
			return self._pin.value

elif 'cpython' == implementation:
	Pin = lambda *args: None


def reverse_byte(a):
	x = ((a & 0x1)  << 7) | ((a & 0x2)  << 5) | \
		((a & 0x4)  << 3) | ((a & 0x8)  << 1) | \
		((a & 0x10) >> 1) | ((a & 0x20) >> 3) | \
		((a & 0x40) >> 5) | ((a & 0x80) >> 7)
	return x
