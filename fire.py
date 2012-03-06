import pygame
from pygame.locals import *
import numpy as np
import random

pygame.init()
screen = pygame.display.set_mode([320, 240])

pal_b = np.empty((256, 4), 'B')
for i in range(256):
    pal_b[i,:] = (i**3/0xFF**2, i**3/0xFF**2, i, 0xFF)
pal = [int(c) for c in pal_b.view('<u4').flatten()]

buf = np.zeros(screen.get_size(), dtype='B', order='F')


while pygame.event.poll().type != KEYDOWN:
    for x in range(320):
        r = random.randrange(0, 2)
        buf[x,239] = 255 if r == 0 else 0;
    buf[1:319,0:239] = (buf[0:318,1:240].astype('uint32') + buf[1:319,1:240] + buf[2:320,1:240]) / 3.1

    screen.lock()
    for y in range(240):
        for x in range(320):
            screen.set_at((x,y), pal[buf[x,y]])
    screen.unlock()

    pygame.display.update()
    #pygame.time.delay(10)

pygame.quit()
