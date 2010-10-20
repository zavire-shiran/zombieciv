import media
import pygame
import math
from OpenGL.GL import *

currentworld = None

def getworld():
    global currentworld
    return currentworld

def transitionto(world):
    global currentworld
    currentworld = world(currentworld)

def drawsquare(pos, size, texture, level=0.0):
    texture()
    glPushMatrix()
    glTranslate(pos[0], pos[1], 0)
    glBegin(GL_QUADS)
    glTexCoord(0.0, 0.0)
    glVertex(0.0, 0.0, level)
    glTexCoord(0.0, 1.0)
    glVertex(0.0, size[1], level)
    glTexCoord(1.0, 1.0)
    glVertex(size[0], size[1], level)
    glTexCoord(1.0, 0.0)
    glVertex(size[0], 0.0, level)
    glEnd()
    glPopMatrix()

def drawhex(pos, size):
    size = float(size)/2
    glPushMatrix()
    glTranslate(pos[0], pos[1], 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex(size, 0)
    glVertex(size/2, size*math.sqrt(3)/2)
    glVertex(-size/2, size*math.sqrt(3)/2)
    glVertex(-size, 0)
    glVertex(-size/2, -size*math.sqrt(3)/2)
    glVertex(size/2, -size*math.sqrt(3)/2)
    glEnd()
    glPopMatrix()
    print (size, 0), (size/2, size*math.sqrt(3)/2), (-size/2, size*math.sqrt(3)/2), (-size, 0), (-size/2, -size*math.sqrt(3)/2), (size/2, -size*math.sqrt(3)/2)



class World:
    def __init__(self, previous = None):
        pass
    def keydown(self, key):
        pass
    def keyup(self, key):
        pass
    def draw(self):
        pass
    def step(self, dt):
        pass

class Opening(World):
    def __init__(self, previous = None):
        self.splash = media.loadtexture('splash.png')
    def keydown(self, key):
        if key == pygame.K_RETURN:
            transitionto(Game)
    def draw(self):
        drawsquare((0,0), (4,3), self.splash)

def drawhexgrid(gridsize, hexsize):
    for x in xrange(gridsize[0]):
        for y in xrange(gridsize[1]):
            if x % 2 == 0:
                drawhex((x * hexsize * 0.75 + 0.25, y * hexsize * math.sqrt(3)/2), hexsize * 0.98)
            else:
                drawhex((x * hexsize * 0.75 + 0.25, y * hexsize * math.sqrt(3)/2 + math.sqrt(3)/4), hexsize * 0.98)

class Game(World):
    def __init__(self, previous = None):
        glDisable(GL_TEXTURE_2D)
    def draw(self):
        drawhexgrid((6, 4), 1)
