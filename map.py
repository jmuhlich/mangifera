import pygame
import numpy
import os
import sys
import random

pygame.init()
screen_size = (640, 480)
screen = pygame.display.set_mode(screen_size)
print pygame.display.Info()

# screen middle x and y
smx = screen_size[0] / 2
smy = screen_size[1] / 2

grid_w, grid_h = 64, 32
grid_w_half = grid_w / 2
grid_h_half = grid_h / 2

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
numpy.random.seed(0)
world_map = numpy.random.randint(4, size=(100,100))
# add a lake
world_map[10:20, 2:6] = 4
# add walls
world_map[15, 8] = 5
world_map[16, 8] = 6
world_map[15, 7] = 7

# index of lowest tile which can't be seen through
min_opaque = 5

# camera movement vectors
camera_right = numpy.array([1, 1], float) / 16
camera_down = numpy.array([1, -1], float) / 16
camera_speed_normal = 1
camera_speed_fast = 10

clock = pygame.time.Clock()


def mainloop():

    keys = {}
    camera = numpy.array([10,10], dtype=float)
    camera_speed = camera_speed_normal
    last_fps_tick = 0

    while True:

        screen.fill(0)

        # render the map
        for wy in range(world_map.shape[1] - 1, -1, -1):
            for wx in range(world_map.shape[0]):

                tile = tiles[world_map[wy,wx]]

                # make wx,wy relative to camera look-at point
                rwx = wx - float(camera[0])
                rwy = wy - float(camera[1])
                # transform into screen space
                sx = smx + (rwx + rwy) * grid_w_half
                sy = smy + (rwx - rwy) * grid_h_half

                # clip to viewport
                if -grid_w < sx < screen_size[0] \
                        and -grid_h < sy < screen_size[1]:
                    # cast a ray to determine visibility
                    if visibility_test(camera, wx, wy):
                        # offset tile properly
                        sx -= tile.get_width() / 2 - 32
                        sy -= tile.get_height() - 31
                        # display on screen
                        screen.blit(tile, (sx, sy))

        # mark camera position
        pygame.draw.circle(screen, pygame.Color('red'), (smx, smy), 5)

        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                keys[event.key] = True
            if event.type == pygame.KEYUP:
                keys[event.key] = False

        # handle key states
        if keys.get(pygame.K_ESCAPE):
            return
        if keys.get(pygame.K_LSHIFT) or keys.get(pygame.K_RSHIFT):
            camera_speed = camera_speed_fast
        else:
            camera_speed = camera_speed_normal
        if keys.get(pygame.K_LEFT):
            camera -= camera_right * camera_speed
        if keys.get(pygame.K_RIGHT):
            camera += camera_right * camera_speed
        if keys.get(pygame.K_UP):
            camera -= camera_down * camera_speed
        if keys.get(pygame.K_DOWN):
            camera += camera_down * camera_speed

        clock.tick(60)
        pygame.display.flip()
        cur_tick = pygame.time.get_ticks()
        if cur_tick >= last_fps_tick + 1000:
            last_fps_tick = cur_tick
            print 'FPS:', clock.get_fps()


def world_to_screen(camera, wx, wy):
    # make wx,wy relative to camera look-at point
    wx -= float(camera[0])
    wy -= float(camera[1])
    # transform into screen space
    sx = smx + (wx + wy) * grid_w_half
    sy = smy + (wx - wy) * grid_h_half
    return sx, sy


def visibility_test(camera, wx, wy):
    """Determine whether camera can 'see' wx,wy via raycasting"""

    # calculate ray position and direction
    #
    # FIXME not sure why the 0.5 is needed but it seems to ensure the rays
    # always intersect the target instead of missing slightly
    ray_pos = camera.copy() + 0.5
    map_target = numpy.array([wx, wy], dtype=float)
    ray_dir = map_target - camera

    # which box of the map we're in
    map_pos = camera.astype(int)

    # length of ray from one x or y-side to next x or y-side
    delta_dist_x = numpy.sqrt(1 + (ray_dir[1] / ray_dir[0]) ** 2)
    delta_dist_y = numpy.sqrt(1 + (ray_dir[0] / ray_dir[1]) ** 2)

    # is the target visible? (assume yes until a wall is hit)
    visible = True

    # calculate step and initial sideDist
    if ray_dir[0] < 0:
        step_x = -1
        side_dist_x = (ray_pos[0] - map_pos[0]) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_pos[0] + 1.0 - ray_pos[0]) * delta_dist_x
    if ray_dir[1] < 0:
        step_y = -1
        side_dist_y = (ray_pos[1] - map_pos[1]) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_pos[1] + 1.0 - ray_pos[1]) * delta_dist_y

    # perform DDA
    while numpy.any(map_pos != map_target):
        # Check if ray has hit a wall (do this before jumping to help ensure the
        # obstruction we hit is itself considered visible)
        if world_map[map_pos[1],map_pos[0]] >= min_opaque:
            visible = False
            break
        # jump to next map square, OR in x-direction, OR in y-direction
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_pos[0] += step_x
        else:
            side_dist_y += delta_dist_y
            map_pos[1] += step_y

    return visible


if __name__ == '__main__':
    mainloop()
    pygame.quit()
