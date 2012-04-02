import pygame
import numpy as np
import os
import sys
import random

def exit_game():
    pygame.quit()
    sys.exit()

tile_base = os.path.join('data', 'base')
tile_names = ('grass', 'dirt', 'sand', 'snow', 'water')
tiles = {}
for name in tile_names:
    path = os.path.join(tile_base, name + '.png')
    tiles[name] = pygame.image.load(path)
print tiles

np.random.seed(0)
world_map = np.random.randint(len(tile_names) - 1, size=(100,100))
#world_map[10:20, 3:7] = len(tile_names) - 1

world_map[0,:] = 0
world_map[1,:] = 1
world_map[2,:] = 2
world_map[3,:] = 3
world_map[4,:] = 0
world_map[5,:] = 1
world_map[6,:] = 2
world_map[7,:] = 3
world_map[:,0] = 0
world_map[:,1] = 1
world_map[:,2] = 2
world_map[:,3] = 3
world_map[:,4] = 4

pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)
print pygame.display.Info()

last_fps_tick = 0
clock = pygame.time.Clock()

keys = {}
camera = [32,16]
camera = [0,0]

while True:
    for y in range(-1,33):
        for x in range(-1,11):
            # FIXME this is still wonky when camera.y&16==16
            wx = x + (camera[0] / 64)
            wy = y + (camera[1] / 16)
            #if x==0 and y==0:
            #    print wx, wy, camera[0], camera[1]
            #    sys.stdout.flush()
            tile = tiles[tile_names[world_map[wy][wx]]]
            sx = x * 64 + (y & 1) * 32 - (camera[0] % 64)
            sy = (y >> 1) * 32 + (y & 1) * 16 - (camera[1] % 16)
            screen.blit(tile, (sx, sy))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        if event.type == pygame.KEYDOWN:
            keys[event.key] = True
        if event.type == pygame.KEYUP:
            keys[event.key] = False
    if keys.get(pygame.K_ESCAPE):
        exit_game()
    if keys.get(pygame.K_LEFT):
        camera[0] -= 1
    if keys.get(pygame.K_RIGHT):
        camera[0] += 1
    if keys.get(pygame.K_UP):
        camera[1] -= 1
    if keys.get(pygame.K_DOWN):
        camera[1] += 1

    #camera[0] = max(camera[0], 32)
    #camera[1] = max(camera[1], 16)


    clock.tick(60)
    pygame.display.flip()
    cur_tick = pygame.time.get_ticks()
    if cur_tick >= last_fps_tick + 1000:
        last_fps_tick = cur_tick
        print 'FPS:', clock.get_fps()
