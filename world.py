import math
import media
import pygame
import texture
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

#I want it to be centering correctly, and it is not.
def drawtext(pos, text):
    text = texture.Text(str(text))
    size = (text.horizsize(0.1), 0.1)
    orig = (pos[0] - size[0]/2.0, pos[1] - size[1]/2.0)
    text()
    glBegin(GL_QUADS)
    glTexCoord(0.0, 0.0)
    glVertex(orig[0], orig[1])
    glTexCoord(1.0, 0.0)
    glVertex(orig[0] + size[0], orig[1])
    glTexCoord(1.0, 1.0)
    glVertex(orig[0] + size[0], orig[1] + size[1])
    glTexCoord(0.0, 1.0)
    glVertex(orig[0], orig[1] + size[1])
    glEnd()

class World:
    def __init__(self, previous = None):
        pass
    def keydown(self, key):
        pass
    def keyup(self, key):
        pass
    def click(self, pos):
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

def hexpos(pos, hexsize):
    x, y = pos
    if x % 2 == 0:
        return (x * hexsize * 0.75 + 0.25 * hexsize,
                y * hexsize * math.sqrt(3)/2 + math.sqrt(3)/4 * hexsize)
    else:
        return (x * hexsize * 0.75 + 0.25 * hexsize,
                y * hexsize * math.sqrt(3)/2)

def drawhexgrid(gridsize, hexsize):
    for x in xrange(gridsize[0]):
        for y in xrange(gridsize[1]):
            drawhex(hexpos((x, y), hexsize), hexsize * 0.98)

#not totally right, has problems on left and right sides of hexagons.
#try closest center next
def worldpos2gridpos(pos, hexsize):
    pos = [x/hexsize for x in pos]
    pos[0] = (pos[0] - 0.25) / 0.75
    pos[0] = int(math.floor(pos[0] + 0.5))
    pos[1] /= math.sqrt(3)/2
    if pos[0] % 2 == 0:
        pos[1] -= 0.5
    pos[1] = int(math.floor(pos[1] + 0.5))
    return pos

def adjacenthexes(pos):
    ret = [(pos[0]+1, pos[1]),
           (pos[0]-1, pos[1]),
           (pos[0],   pos[1]+1),
           (pos[0],   pos[1]-1)]
    if pos[0] % 2 == 0:
        return ret + [(pos[0]-1, pos[1]+1), (pos[0]+1, pos[1]+1)]
    else:
        return ret + [(pos[0]+1, pos[1]-1), (pos[0]-1, pos[1]-1)]

class Game(World):
    def __init__(self, previous = None):
        glDisable(GL_TEXTURE_2D)
        self.hexsize = 0.5
        self.worldstate = [[1000 for y in xrange(8)] for x in xrange(12)]
        self.selected = [0,0]
    def click(self, pos):
        self.selected = worldpos2gridpos(pos, self.hexsize)
    def draw(self):
        glDisable(GL_TEXTURE_2D)
        glColor(1.0, 1.0, 1.0, 1.0)
        drawhexgrid((12, 8), self.hexsize)
        glColor(0.0, 0.0, 0.0, 1.0)
        glTranslate(0.0, 0.0, 1.0)
        drawtext(hexpos(self.selected, self.hexsize), self.worldstate[self.selected[0]][self.selected[1]])
        for (x, y) in adjacenthexes(self.selected):
            drawtext(hexpos((x, y), self.hexsize), self.worldstate[x][y])
