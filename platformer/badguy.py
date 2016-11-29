from sprite import Sprite
import pygame
import sys

class BadGuy(Sprite):
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
                self.addForce('gravity', (0.0, 1.0), 'constant')
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
            self.addForce('baddieleft', (-1.0, 0.0), 'onetime')  
            self.move()
            

        def handleCollisionWith(self, name, other):
            if name == 'boundary' or name == 'solid':
                return True

            if other.kind == 'player':
                print "You are dead!"
                self.world.removeSprite(other)

            return False
