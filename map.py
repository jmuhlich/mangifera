import pygame
import numpy as np
import os
import sys
import random

def exit_game():
    pygame.quit()
    sys.exit()

pygame.init()
screen = pygame.display.set_mode((640, 480))
print pygame.display.Info()

# load tiles
tile_base = 'data'
tile_names = (('base', ('grass', 'dirt', 'sand', 'snow', 'water')),
              ('wall', ('grass-outside-s', 'grass-straight-se',
                        'grass-straight-sw')),
              )
tiles = []
for group, names in tile_names:
    for name in names:
        path = os.path.join(tile_base, group, name + '.png')
        tiles.append(pygame.image.load(path).convert_alpha())

# create random world map
np.random.seed(0)
world_map = np.random.randint(4, size=(100,100))
# add a lake
world_map[10:20, 2:6] = 4
# add walls
world_map[15, 8] = 5
world_map[14, 9] = 6
world_map[14, 8] = 7

last_fps_tick = 0
clock = pygame.time.Clock()

keys = {}
camera = [32,16]

while True:
    # render the map
    for y in range(-1,31):
        for x in range(-1,11):
            wx = x + (camera[0] / 64)
            wy = y + (camera[1] / 16)
            tile = tiles[world_map[wy,wx]]
            # FIXME: this sx/xy math is out of control
            sx = x * 64 + (y & 1) * 32 - (camera[0] % 64) - (camera[1]/16&1)*32 + (camera[1]/16&wy&1)*64
            sy = (y >> 1) * 32 + (y & 1) * 16 - (camera[1] % 16)
            sx -= tile.get_width() / 2 - 32
            sy -= tile.get_height() - 31
            screen.blit(tile, (sx, sy))

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        if event.type == pygame.KEYDOWN:
            keys[event.key] = True
        if event.type == pygame.KEYUP:
            keys[event.key] = False

    # handle key states
    if keys.get(pygame.K_ESCAPE):
        exit_game()
    if keys.get(pygame.K_LEFT):
        camera[0] -= 3
    if keys.get(pygame.K_RIGHT):
        camera[0] += 3
    if keys.get(pygame.K_UP):
        camera[1] -= 3
    if keys.get(pygame.K_DOWN):
        camera[1] += 3

    # keep camera inside the map
    camera[0] = max(camera[0], 32)
    camera[1] = max(camera[1], 16)
    camera[0] = min(camera[0], (world_map.shape[1]-1)*64-screen.get_width())
    camera[1] = min(camera[1], (world_map.shape[0]-1)*16-screen.get_height())

    clock.tick(60)
    pygame.display.flip()
    cur_tick = pygame.time.get_ticks()
    if cur_tick >= last_fps_tick + 1000:
        last_fps_tick = cur_tick
        print 'FPS:', clock.get_fps()
