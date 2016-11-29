from sprite import Sprite
import sys

class Coin(Sprite):
    def __init__(self, world, obj):
        if obj.gid is None:
            print >>sys.stderr, 'Coin: must be created from tile object'
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
                (0.0, 0.0))
        self.count = 0
        self.spin = 0
        self.changed = False

    def paint(self, surface):
        if self.spin == 0:
            gid = self.gid
        elif self.spin == 15:
            gid = self.gid + 12
        elif self.spin == 30:
            gid = self.gid + 24
        else:
            gid = self.gid + 36
        self.paintTile(surface, self.world.data.tiles[gid])

    def game_logic(self, keys, newkeys):
        self.count += 15
        self.spin += 15
        if self.count == 75:
            self.spin = 0
            self.count = 0
            self.changed = not self.changed
