import math
import media
import pygame
import texture
import numpy
import random
from OpenGL.GL import *
from OpenGL.arrays import ArrayDatatype as ADT

currentworld = None
hexbuffer = None
vertexLoc = None
texCoord0Loc = None
normalLoc = None

def getworld():
    global currentworld
    return currentworld

def transitionto(world):
    global currentworld
    currentworld = world(currentworld)

def hexpos(pos, hexsize):
    x, y = pos
    if x % 2 == 0:
        return (x * hexsize * 0.75,
                y * hexsize * math.sqrt(3)/2 + math.sqrt(3)/4 * hexsize)
    else:
        return (x * hexsize * 0.75,
                y * hexsize * math.sqrt(3)/2)

def genhexbuffer(size, hexsize):
    vertbuffer = []
    indexbuffer = []
    ni = 0
    hsize = hexsize * 0.49
    print hsize
    for x in xrange(size[0]):
        for y in xrange(size[1]):
            pos = hexpos((x, y), hexsize)
            vertbuffer += [(hsize + pos[0], pos[1], 0),
                           (hsize/2.0 + pos[0], hsize * math.sqrt(3)/2 + pos[1], 0),
                           (-hsize/2.0 + pos[0], hsize * math.sqrt(3)/2 + pos[1], 0), 
                           (-hsize + pos[0], pos[1], 0),
                           (-hsize/2.0 + pos[0], -hsize * math.sqrt(3)/2 + pos[1], 0),
                           (hsize/2.0 + pos[0], -hsize * math.sqrt(3)/2 + pos[1], 0)]
            indexbuffer += [ni, ni+1, ni+2, 
                            ni, ni+2, ni+3,
                            ni, ni+3, ni+4,
                            ni, ni+4, ni+5]
            ni += 6
    return vertbuffer, indexbuffer

def convertbuffer(buffer):
    return numpy.array(buffer, dtype=numpy.float32)

class buffer:
    def __init__(self, vertbuffer, indexbuffer):
        self.buffer = glGenBuffers(1)
        self.indexbuffer = indexbuffer
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        self.numverts = len(vertbuffer)
        vertbuffer = convertbuffer(vertbuffer)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(vertbuffer), ADT.voidDataPointer(vertbuffer), GL_STATIC_DRAW)
    def __del__(self):
        if glDeleteBuffers:
            glDeleteBuffers(1, [self.buffer])
    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawElementsui(GL_TRIANGLES, self.indexbuffer)
        glDisableClientState(GL_VERTEX_ARRAY)

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

def drawmoveorder(pos):
    glDisable(GL_TEXTURE_2D)
    glColor(0.0, 0.0, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex(pos[0],      pos[1]-0.1,  3.0)
    glVertex(pos[0]+0.07, pos[1]+0.03, 3.0)
    glVertex(pos[0]+0.07, pos[1]+0.03, 3.0)
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


#not totally right, has problems on left and right sides of hexagons.
#try closest center next
def worldpos2gridpos(pos, hexsize):
    pos = [x/hexsize for x in pos]
    pos[0] = (pos[0]) / 0.75
    pos[0] = int(math.floor(pos[0] + 0.5))
    pos[1] /= math.sqrt(3)/2
    if pos[0] % 2 == 0:
        pos[1] -= 0.5
    pos[1] = int(math.floor(pos[1] + 0.5))
    return pos

def adjacenthexes(pos):
    ret = [(pos[0],   pos[1]+1),
           (pos[0],   pos[1]-1)]
    if pos[0] % 2 == 0:
        ret += [(pos[0]+1, pos[1]+1), (pos[0]-1, pos[1]+1)]
    ret += [(pos[0]+1, pos[1]),
            (pos[0]-1, pos[1])]
    if pos[0] % 2 == 1:
        ret += [(pos[0]+1, pos[1]-1), (pos[0]-1, pos[1]-1)]
    return ret

def initworldstate(size):
    ret = [[{'hpop':400*random.random(), 'food':1000, 'military': 0, 'zombie':0,
             'orders':'breed', 'milorders':[False, False, False, False, False, False]}
            for y in xrange(size[1])] for x in xrange(size[0])]
    allhexes = []
    for x in xrange(size[0]):
        for y in xrange(size[1]):
            allhexes += [(x,y)]
    random.shuffle(allhexes)
    for x,y in allhexes[:10]:
        ret[x][y]['zombie'] = 100
#    ret[5][3]['zombie'] = 100
#    ret[5][2]['zombie'] = 100
#    ret[5][4]['zombie'] = 100
#    ret[4][2]['zombie'] = 100
#    ret[4][3]['zombie'] = 100
#    ret[6][2]['zombie'] = 100
#    ret[6][3]['zombie'] = 100
#    ret[5][2]['military'] = 1000
#    ret[5][4]['military'] = 1000
#    ret[4][2]['military'] = 1000
#    ret[4][3]['military'] = 1000
#    ret[6][2]['military'] = 1000
#    ret[6][3]['military'] = 1000

#    ret[5][1]['military'] = 1000
#    ret[4][1]['military'] = 1000
#    ret[3][2]['military'] = 1000
#    ret[3][3]['military'] = 1000
#    ret[3][4]['military'] = 1000
#    ret[4][4]['military'] = 1000
#    ret[5][5]['military'] = 1000
#    ret[6][1]['military'] = 1000
#    ret[7][2]['military'] = 1000
#    ret[7][3]['military'] = 1000
#    ret[7][4]['military'] = 1000
#    ret[6][4]['military'] = 1000
    return ret

class Game(World):
    def __init__(self, previous = None):
        glDisable(GL_TEXTURE_2D)
        self.hexsize = 0.46
        self.size = (11, 7)
        self.worldstate = initworldstate(self.size)
        self.selected = [0,0]
        self.speed = 0
        self.camera = [0.23, 0.15]
        self.camcontrols = {'left': False, 'right': False, 'up': False, 'down': False}
        self.hexbuffer = buffer(*genhexbuffer(self.size, self.hexsize))
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
            self.speed = 5
        if key == pygame.K_4:
            self.speed = 10
        if key == pygame.K_5:
            self.speed = 20
        if key == pygame.K_RIGHT:
            self.camcontrols['right'] = True
        if key == pygame.K_LEFT:
            self.camcontrols['left'] = True
        if key == pygame.K_UP:
            self.camcontrols['up'] = True
        if key == pygame.K_DOWN:
            self.camcontrols['down'] = True
        if key == pygame.K_q:
            self.worldstate[self.selected[0]][self.selected[1]]['milorders'][5] = not self.worldstate[self.selected[0]][self.selected[1]]['milorders'][5]
        if key == pygame.K_w:
            self.worldstate[self.selected[0]][self.selected[1]]['milorders'][1] = not self.worldstate[self.selected[0]][self.selected[1]]['milorders'][1]
        if key == pygame.K_e:
            self.worldstate[self.selected[0]][self.selected[1]]['milorders'][4] = not self.worldstate[self.selected[0]][self.selected[1]]['milorders'][4]
        if key == pygame.K_a:
            self.worldstate[self.selected[0]][self.selected[1]]['milorders'][3] = not self.worldstate[self.selected[0]][self.selected[1]]['milorders'][3]
        if key == pygame.K_s:
            self.worldstate[self.selected[0]][self.selected[1]]['milorders'][0] = not self.worldstate[self.selected[0]][self.selected[1]]['milorders'][0]
        if key == pygame.K_d:
            self.worldstate[self.selected[0]][self.selected[1]]['milorders'][2] = not self.worldstate[self.selected[0]][self.selected[1]]['milorders'][2]
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
#        if self.camcontrols['right']:
#            self.camera[0] -= 1 * dt
#        if self.camcontrols['left']:
#            self.camera[0] += 1 * dt
#        if self.camcontrols['up']:
#            self.camera[1] += 1 * dt
#        if self.camcontrols['down']:
#            self.camera[1] -= 1 * dt
        for i in xrange(self.speed):
            self.worldstep(dt)
    def worldstep(self, dt):
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                tile = self.worldstate[x][y]
                if not tile['zombie'] > 1:
                    normpop = tile['hpop'] / tile['food']
                    tile['hpop'] += normpop * (1 - normpop) * dt * tile['food'] / 10
                    tile['hpop'] = max(0, tile['hpop'])
                normzombies = min(0.95, tile['zombie'] / tile['hpop'])
                humanskilled = normzombies * (1-normzombies) * tile['hpop'] * dt * 0.1
                tile['hpop'] -= humanskilled
                militarykilled = 0.0
                if tile['military'] > 0.0:
                    militarykilled = tile['zombie'] / tile['military'] * dt
                zombieskilled = 0.0
                if tile['military'] > 1.0:
                    zombieskilled += math.log(tile['military']) * dt
                tile['zombie'] += humanskilled - zombieskilled
                tile['military'] -= militarykilled
                if tile['military'] < 0.0:
                    tile['military'] = 0.0
                if tile['zombie'] < 0.1:
                    tile['zombie'] = 0.0
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                adjhexes = zip(range(6), adjacenthexes((x,y)), self.worldstate[x][y]['milorders'])
                random.shuffle(adjhexes)
                for n,adj,milmove in adjhexes:
                    if 0 > adj[0] or adj[0] >= self.size[0] or 0 > adj[1] or adj[1] >= self.size[1]:
                        continue
                    if milmove:
                        milmoved = min(100 * dt, self.worldstate[x][y]['military'])
                        self.worldstate[x][y]['military'] -= milmoved
                        self.worldstate[adj[0]][adj[1]]['military'] += milmoved
                        if self.worldstate[x][y]['military'] == 0.0:
                            self.worldstate[x][y]['milorders'][n] = False
                    if self.worldstate[x][y]['hpop'] - 100 > self.worldstate[adj[0]][adj[1]]['hpop'] and \
                       not self.worldstate[adj[0]][adj[1]]['zombie'] > 0:
                        nummoved = int((self.worldstate[x][y]['hpop'] - self.worldstate[adj[0]][adj[1]]['hpop']) * 0.1)
                        self.worldstate[x][y]['hpop'] -= nummoved
                        self.worldstate[adj[0]][adj[1]]['hpop'] += nummoved
                    if not self.worldstate[x][y]['military'] and \
                       self.worldstate[x][y]['zombie'] > self.worldstate[x][y]['hpop']:
                        nummoved = 0
                        if self.worldstate[adj[0]][adj[1]]['military'] == 0:
                            nummoved = (self.worldstate[x][y]['zombie'] - 
                                        self.worldstate[adj[0]][adj[1]]['zombie']) * dt
                        elif self.worldstate[x][y]['zombie'] > \
                             self.worldstate[x][y]['hpop'] + self.worldstate[adj[0]][adj[1]]['military'] * 0.1:
                            nummoved = self.worldstate[adj[0]][adj[1]]['military'] * 0.1
                        self.worldstate[x][y]['zombie'] -= nummoved
                        self.worldstate[adj[0]][adj[1]]['zombie'] += nummoved
    def draw(self):
        glLoadIdentity()
        glDisable(GL_TEXTURE_2D)
        glTranslate(self.camera[0], self.camera[1], 0.0)
        glColor(1.0, 1.0, 1.0, 1.0)
        self.hexbuffer.draw()

        selectpos = hexpos(self.selected, self.hexsize)
        hsize = self.hexsize * 0.48
        glColor(1.0, 0.0, 0.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex(hsize + selectpos[0], selectpos[1], 1)
        glVertex(hsize/2.0 + selectpos[0], hsize * math.sqrt(3)/2 + selectpos[1], 1)
        glVertex(-hsize/2.0 + selectpos[0], hsize * math.sqrt(3)/2 + selectpos[1], 1)
        glVertex(-hsize + selectpos[0], selectpos[1], 1)
        glVertex(-hsize/2.0 + selectpos[0], -hsize * math.sqrt(3)/2 + selectpos[1], 1)
        glVertex(hsize/2.0 + selectpos[0], -hsize * math.sqrt(3)/2 + selectpos[1], 1)
        glEnd()

        glTranslate(0.0, 0.0, 1.0)
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                hpos = hexpos((x, y), self.hexsize)
                if int(self.worldstate[x][y]['hpop']) > 0:
                    glColor(0.0, 0.0, 0.0, 1.0)
                    drawtext((hpos[0], hpos[1]-self.hexsize*0.2), int(self.worldstate[x][y]['hpop']))
                if int(self.worldstate[x][y]['military']) > 0:
                    glColor(0.1, 0.1, 0.5, 1.0)
                    drawtext((hpos[0], hpos[1]+self.hexsize*0.2), int(self.worldstate[x][y]['military']))
                if self.worldstate[x][y]['zombie'] > 0:
                    glColor(0.3, 0.1, 0.1, 1.0)
                    drawtext(hpos, str(self.worldstate[x][y]['zombie'])[:4])
                adjhexes = adjacenthexes((x,y))
                for n, moveorder in enumerate(self.worldstate[x][y]['milorders']):
                    if moveorder:
                        adjhexpos = hexpos(adjhexes[n], self.hexsize)
                        pos = ((4*hpos[0] + 3*adjhexpos[0])/7.0, (4*hpos[1] + 3*adjhexpos[1])/7.0)
                        drawtext(pos, 'v')
#                        drawmoveorder(pos)
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
