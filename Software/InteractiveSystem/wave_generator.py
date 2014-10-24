__author__ = 'Matthew'
import math

wave = ""
wave2 = ""
for i in range(32):
    #pt = int(2.5*math.log((math.sin(math.pi*2/32*i-2*math.pi/2)*127 + 127) + 1))
    #pt = int(math.sin(math.pi*2/32*i)*127 + 127)
    pt = int(math.cos(math.pi*2/32*i - math.pi - 1.5*math.pi)*127 + 127)
    wave += (str(pt) + ', ')
    wave2 += (str(pt) + '_')
print(wave)
print(wave2)