import pygame
from pygame.locals import *
import numpy as np
import random

pygame.init()
screen = pygame.display.set_mode((320, 240), 0, 8)

palette = np.zeros((256, 3), 'B')
prange = np.array(range(0, 32))
palette[prange,2] = prange<<1
palette[prange+32,0] = prange<<3
palette[prange+32,2] = 64 - (prange<<1)
palette[prange+64,0] = 255
palette[prange+64,1] = prange<<3
palette[96:,0:2] = 255;
palette[prange+96,2] = prange<<2;
palette[prange+128,2] = 64 + (prange<<2);
palette[prange+160,2] = 128 + (prange<<2);
palette[prange+192,2] = 192 + prange;
palette[prange+224,2] = 224 + prange;
pygame.display.set_palette(palette)

last_fps_tick = 0
clock = pygame.time.Clock()

while pygame.event.poll().type != KEYDOWN:
    pixels = pygame.surfarray.pixels2d(screen)
    for x in range(320):
        r = random.random()
        pixels[x,239] = 255 if r < .4 else 0;
    pixels[1:319,0:239] = np.fmax(((pixels[1:319,0:239].astype('int') +
                                    pixels[0:318,1:240] +
                                    pixels[1:319,1:240] +
                                    pixels[2:320,1:240]) >> 2) - 1,
                                  0)

    clock.tick(60)
    pygame.display.flip()
    cur_tick = pygame.time.get_ticks()
    if cur_tick >= last_fps_tick + 1000:
        last_fps_tick = cur_tick
        print 'FPS:', clock.get_fps()

pygame.quit()
