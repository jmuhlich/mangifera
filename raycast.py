import pygame
import pygame.gfxdraw
import numpy as np
import math
import sys

def exit_game():
    global done
    pygame.quit()
    done = True;

pygame.init()
screen_w = 640
screen_h = 480
screen = pygame.display.set_mode((screen_w, screen_h))
pixels = pygame.surfarray.pixels2d(screen)

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
  
rayDirX = np.zeros(1)
rayDirY = np.zeros(1)

done = False
while not done:
    screen.fill(0)

    for x in range(screen_w):
        # calculate ray position and direction 
        cameraX = 2 * x / float(screen_w) - 1 # x-coordinate in camera space
        rayPosX = posX
        rayPosY = posY
        rayDirX[0] = dirX + planeX * cameraX
        rayDirY[0] = dirY + planeY * cameraX

        # which box of the map we're in  
        mapX = int(rayPosX)
        mapY = int(rayPosY)
       
        # length of ray from current position to next x or y-side
        #sideDistX
        #sideDistY
       
        # length of ray from one x or y-side to next x or y-side
        deltaDistX = math.sqrt(1 + (rayDirY[0] * rayDirY[0]) / (rayDirX[0] * rayDirX[0]))
        deltaDistY = math.sqrt(1 + (rayDirX[0] * rayDirX[0]) / (rayDirY[0] * rayDirY[0]))
        #perpWallDist
       
        # what direction to step in x or y-direction (either +1 or -1)
        #stepX
        #stepY

        hit = 0 # was there a wall hit?
        #side # was a NS or a EW wall hit?

        # calculate step and initial sideDist
        if rayDirX[0] < 0:
            stepX = -1
            sideDistX = (rayPosX - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - rayPosX) * deltaDistX
        if rayDirY[0] < 0:
            stepY = -1
            sideDistY = (rayPosY - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY

        # perform DDA
        while hit == 0:
            # jump to next map square, OR in x-direction, OR in y-direction
            if sideDistX < sideDistY:
                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1
            # Check if ray has hit a wall
            if worldMap[mapX,mapY] > 0:
                hit = 1

        # Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
        if side == 0:
            perpWallDist = abs((mapX - rayPosX + (1 - stepX) / 2) / rayDirX[0])
        else:
            perpWallDist = abs((mapY - rayPosY + (1 - stepY) / 2) / rayDirY[0])

        # Calculate height of line to draw on screen
        lineHeight = abs(int(screen_h / perpWallDist))

        # calculate lowest and highest pixel to fill in current stripe
        drawStart = int(-lineHeight / 2 + screen_h / 2)
        if drawStart < 0:
            drawStart = 0;
        drawEnd = int(lineHeight / 2 + screen_h / 2)
        if drawEnd >= screen_h:
            drawEnd = screen_h - 1

        # choose wall color
        color = colormap.get(worldMap[mapX,mapY], defaultcolor)
       
        # give x and y sides different brightness
        if side == 1:
            color /= color2

        # draw the pixels of the stripe as a vertical line
        pygame.gfxdraw.vline(screen, x, drawStart, drawEnd, color)

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
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
        exit_game()
