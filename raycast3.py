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

#colors = ['red', 'green', 'blue', 'white']
#colormap = dict((i + 1, pygame.Color(c)) for i, c in enumerate(colors))
colors = [
    ('origin', 'blue'),
    ('obstruction', 'red'),
    ('visfront', 'green'),
    ('obscured', 'pink'),
    ('visible', 'white'),
    ('cut', 'gray25'),
    ]
colormap = dict((k, pygame.Color(v)) for k, v in colors)

ray_font = pygame.font.Font(None, 12)

tileSize = min(screen_w / mapWidth, screen_h / mapHeight)
mapOrigin = numpy.array([(screen_w - tileSize * mapWidth) / 2,
                         (screen_h - tileSize * mapHeight) / 2], int)

speedNormal = 5
speedSlow = 1


def mainloop():

    # x and y start position
    camera = numpy.array([4.5, 3.5], dtype=float)
    # allocate this as a numpy array to mask ZeroDivisionErrors
    rayDir = numpy.zeros(2)
    # for timing
    last_fps_tick = 0

    speedFactor = speedNormal
    full_visibility = False
    show_rays = True

    done = False
    while not done:
        screen.fill(0)

        vis_map = visibility_test(camera)
        for wy in range(mapHeight):
            for wx in range(mapWidth):
                sx = mapOrigin[0] + wx * tileSize
                sy = mapOrigin[1] + wy * tileSize
                rect = (sx, sy, tileSize, tileSize)
                #if vis_map[wy, wx] or full_visibility:
                #    screen.fill(color, rect)
                if all(camera.astype('int') == (wx, wy)):
                    color = 'origin'
                elif worldMap[wy, wx]:
                    color = 'obstruction'
                elif vis_map[wy, wx] == 1:
                    color = 'visible'
                elif vis_map[wy, wx] == 2:
                    color = 'obscured'
                elif vis_map[wy, wx] == 3:
                    color = 'visfront'
                else:
                    color = 'cut'
                screen.fill(colormap[color], rect) # XXX
        if show_rays:
            visibility_test(camera, True)


        x0 = mapOrigin[0]
        y0 = mapOrigin[1]
        x1 = x0 + mapWidth * tileSize
        y1 = y0 + mapHeight * tileSize
        for wx in range(mapWidth + 1):
            sx = mapOrigin[0] + wx * tileSize
            pygame.gfxdraw.line(screen, sx, y0, sx, y1, pygame.Color('#C0C0C0'))
        for wy in range(mapHeight + 1):
            sy = mapOrigin[1] + wy * tileSize
            pygame.gfxdraw.line(screen, x0, sy, x1, sy, pygame.Color('#C0C0C0'))

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
        #show_rays = keys[pygame.K_r]
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


raymap_dtype = numpy.dtype(zip(['dx', 'dy', 'ex', 'ey'], [float] * 4))

def visibility_test(origin, show_rays=False):
    """Determine visibility of all map positions by raycasting."""

    def has_ray(x, y):
        return ray_map[y, x]['dx'] != 0 or ray_map[y, x]['dy'] != 0

    vis_map = numpy.zeros(worldMap.shape, dtype=int)

    # worldy, worldx, obstructionx/obstructiony/errorx/errory
    ray_map = numpy.empty(worldMap.shape, dtype=raymap_dtype)
    ray_map.fill(0)

    origin = origin.astype(int)

    ray_map[origin[1], origin[0]] = (0,) * 4
    
    for radius in range(1, 20):
        for dx in range(radius + 1):
            dy = radius - dx
            #if dx == 3 and dy == 1: import ipdb; ipdb.set_trace()
            wx = origin[0] + dx
            wy = origin[1] + dy
            if not (0 <= wx < mapWidth and 0 <= wy < mapHeight):
                continue
            r = ray_map[wy, wx].ravel()
            tile = worldMap[wy, wx]
            cx1 = wx - 1
            cy1 = wy
            cx2 = wx
            cy2 = wy - 1
            hr1 = has_ray(cx1, cy1)
            hr2 = has_ray(cx2, cy2)
            if (not hr1 and not hr2) or (dx == 0 and not hr2) or (dy == 0 and not hr1):
                # all input nodes are propagating in the clear
                vis_map[wy, wx] = 1
                if tile:
                    # current tile is an obstruction
                    r[:] = (dx, dy, 0, 0)
            #elif (dx == 0 and hr2) or (dy == 0 and hr1):
            #    # all input nodes are obscured
            #    r[:] = ('inf', 'inf', 0, 0)
            #elif (hr1 and hr2) and (r['ey'] * 3 >= dx or r['ex'] * 3 >= dy):
            #    # all input nodes are obscured
            #    r[:] = ('inf', 'inf', 0, 0)
            elif hr1:
                rc = ray_map[cy1, cx1]
                r['ex'] = rc['ex'] - dy
                r['ey'] = rc['ey'] + dy
                if r['ey'] * 2 >= dx:
                    # this node is off the line (error too high)
                    vis_map[wy, wx] = 1
                    if tile:
                        r[:] = (dx, dy, 0, 0)
                    else:
                        r['dx'] = rc['dx']
                        r['dy'] = rc['dy']
                else:
                    if tile and dy*rc['dx'] < rc['dy']*dx:
                        # new obstruction with shallower slope takes over (FIXME: is that right?)
                        r[:] = (dx, dy, 0, 0)
                    else:
                        vis_map[wy, wx] = 2
                        r['dx'] = rc['dx']
                        r['dy'] = rc['dy']
            else:  # has_ray(cx2, cy2) must be true
                rc = ray_map[cy2, cx2]
                r['ex'] = rc['ex'] + dx
                r['ey'] = rc['ey'] - dx
                if r['ex'] * 2 >= dy:
                    # this node is off the line (error too high)
                    vis_map[wy, wx] = 1
                    if tile:
                        r[:] = (dx, dy, 0, 0)
                    else:
                        r['dx'] = rc['dx']
                        r['dy'] = rc['dy']
                else:
                    if tile and dy*rc['dx'] > rc['dy']*dx:
                        # new obstruction with steeper slope takes over (FIXME: is that right?)
                        r[:] = (dx, dy, 0, 0)
                    else:
                        vis_map[wy, wx] = 2
                        r['dx'] = rc['dx']
                        r['dy'] = rc['dy']

            if show_rays:
                str1 = '%.1f,%.1f' % (r['dx'], r['dy'])
                str2 = '%.1f,%.1f' % (r['ex'], r['ey'])
                sx = wx * tileSize + mapOrigin[0] + 2
                sy = wy * tileSize + mapOrigin[1] + 2
                tsurf = ray_font.render(str1, True, (80,80,80,255))
                screen.blit(tsurf, (sx, sy))
                tsurf = ray_font.render(str2, True, (80,80,80,255))
                screen.blit(tsurf, (sx, sy + ray_font.get_height() + 1))

    return vis_map


def darken(base_color):
    h, s, l, a = base_color.hsla
    new_color = pygame.Color(0)
    new_color.hsla = h, s, l / 4.0, a
    return new_color


if __name__ == '__main__':
    mainloop()
    pygame.quit()
