import pygame
import pygame.gfxdraw
import numpy as np
import math
import sys

pygame.init()
screen_w = 640
screen_h = 480
screen = pygame.display.set_mode((screen_w, screen_h))

last_fps_tick = 0
clock = pygame.time.Clock()

keys = {}


mapWidth = 24
mapHeight = 24

worldMap = np.array([
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
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,0,0,0,5,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ], dtype=np.int)

colors = ['red', 'green', 'blue', 'white']
colormap = dict((i + 1, pygame.Color(c)) for i, c in enumerate(colors))
defaultcolor = pygame.Color('yellow')
color2 = pygame.Color(2, 2, 2, 1)

# x and y start position
posX = 22
posY = 12

#initial direction vector
dirX = -1
dirY = 0

# the 2d raycaster version of camera plane
planeX = 0
planeY = 0.66
  
def mainloop():
    global screen_w, screen_h, screen, last_fps_tick, clock, keys
    global mapWidth, mapHeight, worldMap, colors, colormap, defaultcolor
    global color2, posX, posY, dirX, dirY, planeX, planeY

    x = np.arange(0, screen_w, 1)
    cameraX = 2.0 * x / screen_w - 1 # x-coordinate in camera space
    stepX = np.empty(x.shape, dtype='int')
    stepY = np.empty(x.shape, dtype='int')
    sideDistX = np.empty(x.shape, dtype='float')
    sideDistY = np.empty(x.shape, dtype='float')
    perpWallDist = np.empty(x.shape, dtype='float')
    side = np.empty(x.shape, dtype='int')

    done = False
    while not done:
        screen.fill(0)

        # calculate ray position and direction 
        rayPosX = np.empty(x.shape)
        rayPosX.fill(posX)
        rayPosY = np.empty(x.shape)
        rayPosY.fill(posY)
        rayDirX = dirX + planeX * cameraX
        rayDirY = dirY + planeY * cameraX

        # which box of the map we're in
        mapX = rayPosX.astype('int')
        mapY = rayPosY.astype('int')

        # length of ray from one x or y-side to next x or y-side
        deltaDistX = (1 + rayDirY**2 / rayDirX[0]**2) ** 0.5
        deltaDistY = (1 + rayDirX**2 / rayDirY[0]**2) ** 0.5

        # track wall hits
        hit = np.empty(x.shape, dtype='bool')
        hit.fill(False)

        # calculate step and initial sideDist
        xneg = rayDirX < 0
        n_xneg = np.logical_not(xneg)
        stepX[xneg] = -1
        stepX[n_xneg] = 1
        sideDistX[xneg] = ((rayPosX - mapX) * deltaDistX)[xneg]
        sideDistX[n_xneg] = ((mapX + 1.0 - rayPosX) * deltaDistX)[n_xneg]
        yneg = rayDirY < 0
        n_yneg = np.logical_not(yneg)
        stepY[yneg] = -1
        stepY[n_yneg] = 1
        sideDistY[yneg] = ((rayPosY - mapY) * deltaDistY)[yneg]
        sideDistY[n_yneg] = ((mapY + 1.0 - rayPosY) * deltaDistY)[n_yneg]

        # perform DDA
        for i in range(len(x)):
            while not hit[i]:
                # jump to next map square, OR in x-direction, OR in y-direction
                if sideDistX[i] < sideDistY[i]:
                    sideDistX[i] += deltaDistX[i]
                    mapX[i] += stepX[i]
                    side[i] = 0
                else:
                    sideDistY[i] += deltaDistY[i]
                    mapY[i] += stepY[i]
                    side[i] = 1
                # Check if ray has hit a wall
                if worldMap[mapX[i],mapY[i]] > 0:
                    hit[i] = True

        # Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
        perpWallDist[side==0] = np.absolute((mapX - rayPosX + (1 - stepX) / 2) / rayDirX)[side==0]
        perpWallDist[side==1] = np.absolute((mapY - rayPosY + (1 - stepY) / 2) / rayDirY)[side==1]

        # Calculate height of line to draw on screen
        lineHeight = np.absolute((screen_h / perpWallDist).astype('int'))

        # calculate lowest and highest pixel to fill in current stripe
        drawStart = np.fmax((-lineHeight / 2 + screen_h / 2).astype('int'), 0)
        drawEnd = np.fmin((lineHeight / 2 + screen_h / 2).astype('int'), screen_h - 1)

        for i in range(len(x)):
            # choose wall color
            color = colormap.get(worldMap[mapX[i],mapY[i]], defaultcolor)

            # give x and y sides different brightness
            if side[i] == 1:
                color /= color2

            # draw the pixels of the stripe as a vertical line
            pygame.gfxdraw.vline(screen, x[i], drawStart[i], drawEnd[i], color)

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
        moveSpeed = frameTime * 5.0 # the constant value is in squares/second
        rotSpeed = frameTime * 3.0 # the constant value is in radians/second

        # handle key states
        if keys.get(pygame.K_UP):
            # move forward if no wall in front of you
            if not worldMap[posX + dirX * moveSpeed, posY]:
                posX += dirX * moveSpeed
            if not worldMap[posX, posY + dirY * moveSpeed]:
                posY += dirY * moveSpeed
        if keys.get(pygame.K_DOWN):
            # move backwards if no wall behind you
            if not worldMap[posX - dirX * moveSpeed, posY]:
                posX -= dirX * moveSpeed
            if not worldMap[posX, posY - dirY * moveSpeed]:
                posY -= dirY * moveSpeed
        if keys.get(pygame.K_RIGHT):
            # rotate to the right   
            # both camera direction and camera plane must be rotated
            oldDirX = dirX;
            dirX = dirX * math.cos(-rotSpeed) - dirY * math.sin(-rotSpeed)
            dirY = oldDirX * math.sin(-rotSpeed) + dirY * math.cos(-rotSpeed)
            oldPlaneX = planeX
            planeX = planeX * math.cos(-rotSpeed) - planeY * math.sin(-rotSpeed)
            planeY = oldPlaneX * math.sin(-rotSpeed) + planeY * math.cos(-rotSpeed)
        if keys.get(pygame.K_LEFT):
            # rotate to the left
            # both camera direction and camera plane must be rotated
            oldDirX = dirX
            dirX = dirX * math.cos(rotSpeed) - dirY * math.sin(rotSpeed)
            dirY = oldDirX * math.sin(rotSpeed) + dirY * math.cos(rotSpeed)
            oldPlaneX = planeX
            planeX = planeX * math.cos(rotSpeed) - planeY * math.sin(rotSpeed)
            planeY = oldPlaneX * math.sin(rotSpeed) + planeY * math.cos(rotSpeed)
        if keys.get(pygame.K_ESCAPE):
            done = True

if __name__ == '__main__':
    mainloop()
    pygame.quit()
