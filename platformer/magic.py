from sprite import Sprite
import pygame
import sys

class Magic(Sprite):
	def __init__(self, world, obj):
		if obj.gid is None:
			print >>sys.stderr, 'BadGuy: must be created from tile object'
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
                self.count = 0
                self.walk = False

        def paint(self, surface):
                gid = self.gid
                if self.dx == 0:
                        gid = 5478
                if self.dx < 0:
                        gid = self.gid + 1
                if self.dx > 0:
                        gid = self.gid - 172*2

                if self.walk:
                        gid = self.gid
                else:
                        gid = self.gid + 1

                self.paintTile(surface, self.world.data.tiles[gid])

        def game_logic(self, keys, newkeys): 
            self.addForce('magicmove', (2.0, 0.0), 'onetime')  
            self.move()

        def setx(self, x):
            self.x = x

        def sety(self, y):
            self.y = y

        def handledirection(self, direction):
            if direction == 'left':
                self.d = (-2.0, 0.0)
            if direction == 'right':
                self.d = (2.0, 0.0)
            return self.d 

            

        def handleCollisionWith(self, name, other):
            if name == 'boundary' or name == 'solid':
                self.world.removeSprite(self)
                return True

            if other.kind == 'badguy':
                print "dead!"
                self.world.removeSprite(other)
                self.world.removeSprite(self)

            return False
