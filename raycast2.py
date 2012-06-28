import pygame
import pygame.gfxdraw
import numpy
import math
import sys
import collections

pygame.init()
screen_w = 1000
screen_h = 1000
screen = pygame.display.set_mode((screen_w, screen_h))

clock = pygame.time.Clock()

keys = collections.defaultdict(lambda: False)


mapWidth = 24
mapHeight = 24

worldMap = numpy.array([
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,2,2,2,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
        [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,3,0,0,0,3,0,0,0,1],
        [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,2,2,0,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,0,0,0,4,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ], dtype=int)

colors = ['red', 'green', 'blue', 'white']
colormap = dict((i + 1, pygame.Color(c)) for i, c in enumerate(colors))
defaultcolor = pygame.Color('#808080')
color2 = pygame.Color(2, 2, 2, 1)

tileSize = min(screen_w / mapWidth, screen_h / mapHeight)
mapOrigin = numpy.array([(screen_w - tileSize * mapWidth) / 2,
                         (screen_h - tileSize * mapHeight) / 2], int)

speedNormal = 5
speedSlow = 1


def mainloop():

    # x and y start position
    camera = numpy.array([22.5, 12.5], dtype=float)
    # allocate this as a numpy array to mask ZeroDivisionErrors
    rayDir = numpy.zeros(2)
    # for timing
    last_fps_tick = 0

    speedFactor = speedNormal
    full_visibility = False
    show_rays = False

    done = False
    while not done:
        screen.fill(0)

        vis_map = visibility_test(camera)
        for wy in range(mapHeight):
            for wx in range(mapWidth):
                sx = mapOrigin[0] + wx * tileSize
                sy = mapOrigin[1] + wy * tileSize
                color = colormap.get(worldMap[wy, wx], defaultcolor)
                rect = (sx, sy, tileSize, tileSize)
                if vis_map[wy, wx] or full_visibility:
                    screen.fill(color, rect)
        if show_rays:
            visibility_test(camera, True)

        # mark camera position
        camera_screen = (camera * tileSize + mapOrigin).astype(int)
        pygame.draw.circle(screen, pygame.Color('yellow'), camera_screen, 5)
        pygame.draw.circle(screen, pygame.Color('purple'), camera_screen, 5, 1)

        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                keys[event.key] = True
            if event.type == pygame.KEYUP:
                keys[event.key] = False

        #frameTime = clock.tick(60)
        frameTime = clock.tick(0) / 1000.0 # seconds
        pygame.display.flip()
        cur_tick = pygame.time.get_ticks()
        if cur_tick >= last_fps_tick + 1000:
            last_fps_tick = cur_tick
            print 'FPS:', clock.get_fps()

        # speed modifiers
        moveSpeed = frameTime * speedFactor  # adjust for frame rate

        # handle key states
        show_rays = keys[pygame.K_r]
        full_visibility = keys[pygame.K_v]
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speedFactor = speedSlow
        else:
            speedFactor = speedNormal
        if keys[pygame.K_UP]:
            new_y = camera[1] - moveSpeed
            if not worldMap[new_y, camera[0]]:
                camera[1] = new_y
        if keys[pygame.K_DOWN]:
            new_y = camera[1] + moveSpeed
            if not worldMap[new_y, camera[0]]:
                camera[1] = new_y
        if keys[pygame.K_LEFT]:
            new_x = camera[0] - moveSpeed
            if not worldMap[camera[1], new_x]:
                camera[0] = new_x
        if keys[pygame.K_RIGHT]:
            new_x = camera[0] + moveSpeed
            if not worldMap[camera[1], new_x]:
                camera[0] = new_x
        if keys[pygame.K_ESCAPE]:
            done = True


def visibility_test(origin, show_rays=False):
    """Determine visibility of all map positions by raycasting."""

    vis_map = numpy.zeros_like(worldMap)

    num_targets = (numpy.sum(worldMap.shape) - 2) * 2
    targets = numpy.empty((num_targets, 2))
    i = 0
    for wx in numpy.arange(worldMap.shape[1]) + 0.5:
        for wy in [0.5, worldMap.shape[0] - 0.5]:
            targets[i] = [wx, wy]
            i += 1
    for wy in numpy.arange(1, worldMap.shape[0] - 1) + 0.5:
        for wx in [0.5, worldMap.shape[1] - 0.5]:
            targets[i] = [wx, wy]
            i += 1
    p1 = numpy.round(mapOrigin + origin * tileSize).astype(int)

    for target in targets:

        ray_dir = target - origin

        # which box of the map we're in
        map_pos = numpy.floor(origin).astype(int)

        # length of ray from one x or y-side to next x or y-side
        delta_dist_x = numpy.sqrt(1 + (ray_dir[1] / ray_dir[0]) ** 2)
        delta_dist_y = numpy.sqrt(1 + (ray_dir[0] / ray_dir[1]) ** 2)

        # calculate step and initial sideDist
        if ray_dir[0] < 0:
            step_x = -1
            side_dist_x = (origin[0] - map_pos[0]) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_pos[0] + 1.0 - origin[0]) * delta_dist_x
        if ray_dir[1] < 0:
            step_y = -1
            side_dist_y = (origin[1] - map_pos[1]) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_pos[1] + 1.0 - origin[1]) * delta_dist_y

        # perform DDA
        while 0 <= map_pos[0] < worldMap.shape[1] and 0 <= map_pos[1] < worldMap.shape[0]:
            # mark current location as visible
            vis_map[map_pos[1], map_pos[0]] = True
            # break if we hit a wall
            if worldMap[map_pos[1], map_pos[0]]:
                if side == 0:
                    hit_dist = abs((map_pos[0] - origin[0] + (1 - step_x) / 2) / ray_dir[0])
                else:
                    hit_dist = abs((map_pos[1] - origin[1] + (1 - step_y) / 2) / ray_dir[1])
                hit_pos = origin + ray_dir * hit_dist
                break
            # jump to next map square, OR in x-direction, OR in y-direction
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_pos[0] += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_pos[1] += step_y
                side = 1
        if show_rays:
            p2 = numpy.round(mapOrigin + hit_pos * tileSize).astype(int)
            p3 = numpy.round(mapOrigin + target * tileSize).astype(int)
            pygame.gfxdraw.line(screen, p1[0], p1[1], p2[0], p2[1],
                                pygame.Color('#C0C0C0'))
            pygame.gfxdraw.line(screen, p2[0], p2[1], p3[0], p3[1],
                                pygame.Color('#404040'))


    return vis_map


if __name__ == '__main__':
    mainloop()
    pygame.quit()
