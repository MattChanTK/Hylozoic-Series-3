__author__ = 'Matthew'
import math


for j in range(4):
    wave = ""
    wave2 = ""
    for i in range(32):
        #pt = int(2.5*math.log((math.sin(math.pi*2/32*i-2*math.pi/2)*127 + 127) + 1))
        #pt = int(math.sin(math.pi*2/32*i)*127 + 127)
        pt = max(int(42*(math.exp(math.cos(math.pi*2/32*i - math.pi - 0.25*j*math.pi)+1)-3.5)), 0)
        wave += (str(pt) + ', ')
        wave2 += (str(pt) + '_')
    print(wave)
    print(wave2)