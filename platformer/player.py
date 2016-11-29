from sprite import Sprite
from magic import *
import pygame
import sys

class Player(Sprite):
    def __init__(self, world, obj):
        if obj.gid is None:
            print >>sys.stderr, 'Player: must be created from tile object'
            sys.exit(1)

        self.world = world
        self.gid = obj.gid
        tile = world.data.tiles[self.gid]

        Sprite.__init__(self,
                world,
                obj.kind,
                '{} ({},{})'.format(obj.kind, obj.x, obj.y),
                tile.get_width(), tile.get_height(),
                obj.x, obj.y,
                (16.0, 16.0))
        self.addForce('friction', (1.0, 0.0), 'slowdown')
        self.addForce('gravity', (0.0, 1.0), 'constant')
        self.count = 0
        self.walk = False
        self.coincount = 0
        self.face = "word"
        pygame.init()
        self.coinsound = pygame.mixer.Sound("coin.wav")

    def paint(self, surface):
        gid = self.gid
        if self.dx == 0:
            gid = 3251-1
        if self.dx < 0:
            gid = self.gid - 172
            self.face = 'left'
        if self.dx > 0:
            gid = self.gid + 172
            self.face = 'right'

        if self.walk:
            gid = self.gid
        else:
            gid = self.gid + 1

        self.paintTile(surface, self.world.data.tiles[gid])

    def game_logic(self, keys, newkeys):
        self.count += 1
        if self.count == 10:
            self.count = 0
        if pygame.K_UP in newkeys:
            if self.dy == 0:
                self.addForce('uparrow', (0.0, -20.0), 'onetime')
        if pygame.K_DOWN in keys:
            self.addForce('downarrow', (0.0, 3.0), 'onetime')
        if pygame.K_LEFT in keys:
            self.gid = 3423
            self.walk = not self.walk
            self.addForce('leftarrow', (-3.0, 0.0), 'onetime')

        if pygame.K_RIGHT in keys:
            self.gid = 3079
            self.walk = not self.walk
            self.addForce('rightarrow', (3.0, 0.0), 'onetime')
        # if pygame.K_SPACE in newkeys:
        #     m = self.Magic(world, obj)

        #Move to level 2
        # if self.x == 131 and self.y == 2816:
        #     self.x = 98
        #     self.y = 2175
            


        (x, y) = (self.x, self.y)
        self.move()

        # move the world to match our motion
        (dx, dy) = (self.x - x, self.y - y)
        self.world.x += dx
        self.world.y += dy

    def handleCollisionWith(self, name, other):
        # stop when we hit a wall/edge
        if name == 'boundary' or name == 'solid':
            return True

        if other.kind == 'coin':
            self.coinsound.play()
            print 'I got a coin!'
            self.coincount += 1
            print self.coincount
            self.world.removeSprite(other)

        if other.kind == 'badguy':
            #print "You are dead!"
            self.world.removeSprite(self)

        return False
