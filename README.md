# micropython-gu7000

A python library for Noritake GU7000 series VFDs. Adapted from the Arduino version.

It should work fine on both CircuitPython and MicroPython.

Current status: alpha, testing, just-work

## Intro

Well, I just said, this is a lib for GU7000 series, but in python.

## Usage

TBW. See `test_on_cpy.py`.

(Just provide an object that has `write` attribute and can accept bytes or
similar things)

## Notes

- The bitmap image is artwork from PiSugar.
- A script(`bitmap_convert.py`) is provided to generate the correct image data
  for the VFD.
    - The binary form of the image is: `[width][height][data]`, the width and
      height takes one byte each, and the length of the data equals
      `width*height//8`.
- The display's speed of processing the input data is pretty slow, and an async
  lib would be better utilizing the SPI bus.
