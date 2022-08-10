
# ImageMemoryArea
FlashImageArea =  1
ScreenImageArea = 2

# ScrollMode
WrappingMode =    1
VertScrollMode =  2
HorizScrollMode = 3

# CompositionMode
NormalCompositionMode = 0
OrCompositionMode =     1
AndCompositionMode =    2
XorCompositionMode =    3

# ScreenSaver
AllDotsOffSaver = 2
AllDotsOnSaver =  3
InvertSaver =   4

# LEDColor
NoLight =       0x000
BlueLight =     0x00f
GreenLight =    0x0f0
CyanLight =     0x0ff
RedLight =      0xf00
MagentaLight =  0xf0f
SmokeLight =    0xfff

# FontFormat
GU70005x7Format =0
GU70007x8Format =1
CUUFormat =    2
LCDFormat =    CUUFormat


def get_column(data, col):
	out = 0
	for i in range(8):
		if (data[i] & (1<<(4-col))):
			out += 1 << (7-i)
	return out


class GU7000Display:

	def __init__(self, width, height, *args, model=None, interface=None, **kwargs):
		self.width = width
		self.height = height
		self.model = model if model else "7000"
		self._interface = interface

	@property
	def height(self):
		return self._height

	@height.setter
	def height(self, value):
		self._height = value
		self._lines = value // 8
	
	def _command(self, *args):
		# write bytes
		if len(args) == 1:
			self._interface.write(args[0])
		else:
			self._interface.write(bytes(args))

	def _command_us(self, *args):
		self._command(0x1f, 0x28, *args)

	def _command_xy(self, x, y):
		self._command(x)
		self._command(x>>8)
		y //= 8
		self._command(y)
		self._command(y>>8)

	def _command_xy_nodiv(self, x, y):
		self._command(x)
		self._command(x>>8)
		self._command(y)
		self._command(y>>8)

	def back(self):
		self._command(0x08)

	def forward(self):
		self._command(0x09)

	def line_feed(self):
		self._command(0x0a)

	def home(self):
		self._command(0x0b)

	def carriage_return(self):
		self._command(0x0d)

	def crlf(self):
		self.carriage_return()
		self.line_feed()

	def set_cursor(self, x, y):
		self._command(0x1f)
		self._command(b'$')
		self._command_xy(x, y)

	def clear(self):
		self._command(0x0c)

	def cursor_on(self):
		self._command(0x1f, ord('C'), 1)

	def cursor_off(self):
		self._command(0x1f, ord('C'), 0)

	def init(self):
		# don't call it if you don't hard reset the display
		self._interface.init()
		self._command(0x1b)
		self._command(b'@')

	def reset(self):
		self._interface.hard_reset()

	def use_multibyte_chars(self, enable):
		if self.model[1] == '9':
			self._command_us(ord('g'), 0x02)
			self._command(enable)

	def set_multibyte_charset(self, code):
		if self.model[1] == '9':
			self._command_us(ord('g'), 0x0f)
			self._command(code)

	def use_custom_chars(self, enable):
		self._command(0x1b, ord('%'), enable)

	def define_custom_char(self, code, font_format, data):
		self._command(0x1b, ord('&'), 0x01)
		self._command(code)
		self._command(code)

		if font_format == CUUFormat:
			self._command(5)
			for i in range(5):
				self._command(get_column(data, i))
		elif font_format == GU70005x7Format:
			self._command(5)
			self.vfd_print(data, length=5)
		elif font_format == GU70007x8Format:
			self._command(7)
			self.vfd_print(data, 7)

	def delete_custom_char(self, code):
		self._command(0x1b, ord('?'), 0x01)
		self._command(code)

	def set_ascii_variant(self, code):
		if code < 0x0d:
			self._command(0x1b, ord('R'), code)

	def set_charset(self, code):
		if code < 0x05 or (0x10 <= code <= 0x13):
			self._command(0x1b, ord('t'), code)

	def set_scroll_mode(self, mode):
		self._command(0x1f, mode)

	def set_horiz_scroll_speed(self, speed):
		self._command(0x1f, ord('s'), speed)

	def invert_on(self, mode):
		self._command(0x1f, ord('b'), 1)

	def invert_off(self, mode):
		self._command(0x1f, ord('b'), 0)

	def set_composition_mode(self, mode):
		self._command(0x1f, ord('w'), mode)

	def set_brightness(self, level):
		if level == 0:
			self.turn_off()
		elif level <= 100:
			self.turn_on()
			self.command(0x1f, ord('X'), (level * 10 + 120) // 125)

	def wait(self, time):
		self._command_us(ord('a'), 0x01)
		self._command(time)

	def scroll(self, x, y, count, speed):
		pos = (x * self._lines) + (y / 8)
		self._command_us(ord('a'), 0x10)
		self._command(pos, pos>>8, times, times>>8, speed)

	def blink(self, enable=0, reverse=0, on_time=0, off_time=0, times=0):
		reverse = reverse & enable
		flag = (reverse << 1) | enable
		self._command_us(ord('a'), 0x11, flag, on_time, off_time, times)

	def turn_on(self):
		self._command_us(ord('a'), 0x40, 0x01)

	def turn_off(self):
		self._command_us(ord('a'), 0x40, 0x00)

	def screensaver(self, mode):
		self._command_us(ord('a'), 0x40, mode)

	def draw_image(self, width=0, height=0, x=0, y=0, data=None, file_obj=None):
		assert data is not None or file_obj is not None, 'Must provide data or a file object!'

		self.set_cursor(x, y)
		
		if data:
			assert width > 0
			assert height > 0
			if height > self.height:
				return
			self._command_us(ord('f'), 0x11)
			self._command_xy(width, height)
			self._command(1)
			self._command(data)
		elif file_obj:
			if not hasattr(file_obj, 'read'):
				raise AttributeError('The provided file object does not has a "read" method!')
			if not hasattr(file_obj, 'seek'):
				raise AttributeError('The provided file object does not has a "seek" method!')
			file_obj.seek(0)
			width, height = file_obj.read(2)
			if height > self.height:
				return
			self._command_us(ord('f'), 0x11)
			self._command_xy(width, height)
			
			data = bytes([1])  # initial data
			while len(data) > 0:
				self._command(data)
				data = file_obj.read(16)

	def set_font_style(self, propotional=0, even_spacing=0):
		self._command_us(ord('g'), 0x03, (propotional << 1) | even_spacing)

	def set_font_size(self, x, y, tall=0):
		if x <= 4 and y <= 2:
			self._command_us(ord('g'), 0x40, x, y)
			if (self.model[1] == '9'):
				self._command_us(ord('g'), 0x01, tall+1)

	def select_window(self, window):
		if window <= 4:
			self._command(0x10 & window)

	def define_window(self, window, x, y, width, height):
		self._command_us(ord('w'), 0x02, window, 0x01)
		self._command_xy(x, y)
		self._command_xy(width, height)

	def delete_window(self, window):
		self._command_us(ord('w'), 0x02, window, 0x00)
		self._command_xy(0, 0)
		self._command_xy(0, 0)

	def join_screens(self):
		self._command_us(ord('w'), 0x10, 0x01)

	def separate_screens(self):
		self._command_us(ord('w'), 0x10, 0x00)

	def vfd_print(self, data, length=None):
		if isinstance(data, int):
			self._command(data)
		else:
			self._command(data[:length])

