# This app will encode or decode text messages in an image file.
# The app will use RGB channels so only PNG files will be accepted.
# This technique will focus on Least Signifigant Bit (LSB) encoding.

from PIL import Image
import os

def encode(img, msg):
  # LSB-encode: store message length in red of (0,0), then 8 bits/char across 3 pixels/char
  pixels = img.load()
  width, height = img.size
  letterSpot = 0
  pixel = 0
  letterBinary = ""
  msgLength = len(msg)

  # store length (0–255) in red channel of first pixel
  red, green, blue = pixels[0, 0]
  pixels[0, 0] = (min(255, msgLength), green, blue)

  for i in range(msgLength * 3):
    x = i % width
    y = i // width

    red, green, blue = pixels[x, y]
    redBinary = numberToBinary(red)
    greenBinary = numberToBinary(green)
    blueBinary = numberToBinary(blue)

    if pixel % 3 == 0:
      letterBinary = numberToBinary(ord(msg[letterSpot]))
      # ignore red on the first pixel of each letter
      greenBinary = greenBinary[0:7] + letterBinary[0]
      blueBinary  = blueBinary[0:7]  + letterBinary[1]

    elif pixel % 3 == 1:
      redBinary   = redBinary[0:7]   + letterBinary[2]
      greenBinary = greenBinary[0:7] + letterBinary[3]
      blueBinary  = blueBinary[0:7]  + letterBinary[4]

    else:
      redBinary   = redBinary[0:7]   + letterBinary[5]
      greenBinary = greenBinary[0:7] + letterBinary[6]
      blueBinary  = blueBinary[0:7]  + letterBinary[7]
      letterSpot += 1

    red   = binaryToNumber(redBinary)
    green = binaryToNumber(greenBinary)
    blue  = binaryToNumber(blueBinary)

    pixels[x, y] = (red, green, blue)
    pixel += 1

  img.save("secretImg.png", "PNG")

def decode(img):
  """Reads the least significant bit from RGB channels and rebuilds the message."""
  msg = ""
  pixels = img.load()
  red, green, blue = pixels[0, 0]
  msgLength = red  # we stored length in red channel of (0,0)

  width, height = img.size
  pixel = 0
  letterBinary = ""
  x = 0
  y = 0

  while len(msg) < msgLength:
    red, green, blue = pixels[x, y]
    redBinary   = numberToBinary(red)
    greenBinary = numberToBinary(green)
    blueBinary  = numberToBinary(blue)

    if pixel % 3 == 0:
      letterBinary = greenBinary[7] + blueBinary[7]
    elif pixel % 3 == 1:
      letterBinary = letterBinary + redBinary[7] + greenBinary[7] + blueBinary[7]
    else:
      letterBinary = letterBinary + redBinary[7] + greenBinary[7] + blueBinary[7]
      letterAscii = binaryToNumber(letterBinary)
      msg += chr(letterAscii)
      # (optional) letterBinary will be overwritten at next pixel % 3 == 0

    pixel += 1
    x = pixel % width
    y = pixel // width

  return msg

# Helper functions

def numberToBinary(num):
  """Convert 0–255 integer to an 8-bit binary string."""
  # clamp to be safe
  num = max(0, min(255, int(num)))
  return format(num, '08b')

def binaryToNumber(bin_str):
  """Convert 8-bit binary string to 0–255 integer."""
  # tolerate shorter/longer by slicing/padding
  s = ''.join(c for c in str(bin_str) if c in '01')
  if len(s) < 8:
    s = s.zfill(8)
  elif len(s) > 8:
    s = s[-8:]
  return int(s, 2)

def main():
  # Encode example
  myImg = Image.open('pki.png')   # make sure this file exists
  myMsg = "This is a secret message I will hide in an image."
  encode(myImg, myMsg)
  myImg.close()

  # Decode example
  yourImg = Image.open('secretImg.png')
  msg = decode(yourImg)
  print(msg)
  yourImg.close()

if __name__ == '__main__':
  main()
