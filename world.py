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
    glTexCoord(text.bounds[0], 0.0)
    glVertex(orig[0] + size[0], orig[1])
    glTexCoord(text.bounds[0], text.bounds[1])
    glVertex(orig[0] + size[0], orig[1] + size[1])
    glTexCoord(0.0, text.bounds[1])
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
        return (x * hexsize * 0.75,
                y * hexsize * math.sqrt(3)/2 + math.sqrt(3)/4 * hexsize)
    else:
        return (x * hexsize * 0.75,
                y * hexsize * math.sqrt(3)/2)

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

def initworldstate(size):
    ret = [[{'hpop':0, 'food':1000} for y in xrange(8)] for x in xrange(12)]
    ret[3][3]['hpop'] = 20
    return ret

class Game(World):
    def __init__(self, previous = None):
        glDisable(GL_TEXTURE_2D)
        self.hexsize = 0.5
        self.size = (12, 8)
        self.worldstate = initworldstate(self.size)
        self.selected = [0,0]
        self.speed = 1
        self.camera = [0.0, 0.0]
        self.camcontrols = {'left': False, 'right': False, 'up': False, 'down': False}
    def click(self, pos):
        self.selected = worldpos2gridpos((pos[0] - self.camera[0], pos[1] - self.camera[1]), self.hexsize)
    def keydown(self, key):
        if key == pygame.K_0:
            self.speed = 0
        if key == pygame.K_1:
            self.speed = 1
        if key == pygame.K_2:
            self.speed = 2
        if key == pygame.K_3:
            self.speed = 4
        if key == pygame.K_4:
            self.speed = 8
        if key == pygame.K_5:
            self.speed = 16
        if key == pygame.K_RIGHT:
            self.camcontrols['right'] = True
        if key == pygame.K_LEFT:
            self.camcontrols['left'] = True
        if key == pygame.K_UP:
            self.camcontrols['up'] = True
        if key == pygame.K_DOWN:
            self.camcontrols['down'] = True
    def keyup(self, key):
        if key == pygame.K_RIGHT:
            self.camcontrols['right'] = False
        if key == pygame.K_LEFT:
            self.camcontrols['left'] = False
        if key == pygame.K_UP:
            self.camcontrols['up'] = False
        if key == pygame.K_DOWN:
            self.camcontrols['down'] = False
    def step(self, dt):
        if self.camcontrols['right']:
            self.camera[0] -= 1 * dt
        if self.camcontrols['left']:
            self.camera[0] += 1 * dt
        if self.camcontrols['up']:
            self.camera[1] += 1 * dt
        if self.camcontrols['down']:
            self.camera[1] -= 1 * dt
        for i in xrange(self.speed):
            self.worldstep(dt)
    def worldstep(self, dt):
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                tile = self.worldstate[x][y]
                normpop = tile['hpop'] / tile['food']
                tile['hpop'] += normpop * (1 - normpop) * dt * tile['food'] / 10
                tile['hpop'] = max(0, tile['hpop'])
                tile['food'] -= (tile['hpop']/tile['food']) * dt * 10
                normfood = tile['food'] / 1000.0
                tile['food'] += normfood * (1 - normfood) * dt * tile['food'] / 10
                tile['food'] = max(10.0, tile['food'])
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                for adj in adjacenthexes((x,y)):
                    if 0 > adj[0] or adj[0] >= 12 or 0 > adj[1] or adj[1] >= 8:
                        continue
                    if self.worldstate[x][y]['hpop'] - 100 > self.worldstate[adj[0]][adj[1]]['hpop']:
                        nummoved = int((self.worldstate[x][y]['hpop'] - self.worldstate[adj[0]][adj[1]]['hpop']) * 0.1)
                        self.worldstate[x][y]['hpop'] -= nummoved
                        self.worldstate[adj[0]][adj[1]]['hpop'] += nummoved
    def draw(self):
        glDisable(GL_TEXTURE_2D)
        glTranslate(self.camera[0], self.camera[1], 0.0)
        glColor(1.0, 1.0, 1.0, 1.0)
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                if self.selected == [x, y]:
                    glColor(1.0, 0.0, 0.0, 1.0)
                else:
                    glColor(1.0, 1.0, 1.0, 1.0)
                drawhex(hexpos((x, y), self.hexsize), self.hexsize * 0.98)
        glTranslate(0.0, 0.0, 1.0)
        for x in xrange(12):
            for y in xrange(8):
                hpos = hexpos((x, y), self.hexsize)
                glColor(0.0, 0.0, 0.0, 1.0)
                drawtext((hpos[0], hpos[1]-self.hexsize*0.2), int(self.worldstate[x][y]['hpop']))
                glColor(0.1, 0.3, 0.1, 1.0)
                drawtext((hpos[0], hpos[1]+self.hexsize*0.2), int(self.worldstate[x][y]['food']))
        glLoadIdentity()
        glTranslate(0.0, 0.0, 2.0)
        glDisable(GL_TEXTURE_2D)
        glColor(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_QUADS)
        glVertex(0.0, 2.9, 0.0)
        glVertex(4.0, 2.9, 0.0)
        glVertex(4.0, 3.0, 0.0)
        glVertex(0.0, 3.0, 0.0)
        glEnd()
        glTranslate(0.0, 0.0, 1.0)
        glColor(1.0, 0.0, 0.0, 1.0)
        drawtext((0.05, 2.95), str(self.speed) + 'x')
