import mapfile
import pygame

class World:
    def __init__(self, data):
        self.data = data
        self.x = 0
        self.y = 0
        self.sprites = {}

        # set up the collision matrix
        self.matrix = []
        (sizex, sizey) = (self.data.width, self.data.height)
        for yy in range(sizey):
            row = []
            for xx in range(sizex):
                row.append({})
            self.matrix.append(row)

    def addSprite(self, sprite):
        
        if sprite.name not in self.sprites:
            self.sprites[sprite.name] = sprite
            self.addToCollisionMatrix(sprite)

    def removeSprite(self, sprite):
        
        if sprite.name in self.sprites:
            del self.sprites[sprite.name]
            self.removeFromCollisionMatrix(sprite)

    def addToCollisionMatrix(self, sprite):
       
        if sprite.name not in self.sprites:
            return
        (tilesizex, tilesizey) = (self.data.tilewidth, self.data.tileheight)
        (sizex, sizey) = (self.data.width, self.data.height)
        for (x, y) in sprite.getPoints():
            xx, yy = int(x) / tilesizex, int(y) / tilesizey
            if xx < 0 or xx >= sizex or yy < 0 or yy >= sizey:
                continue
            self.matrix[yy][xx][sprite.name] = sprite

    def removeFromCollisionMatrix(self, sprite):
        
        (sizex, sizey) = (self.data.width, self.data.height)
        (tilesizex, tilesizey) = (self.data.tilewidth, self.data.tileheight)
        for (x, y) in sprite.getPoints():
            xx, yy = int(x) / tilesizex, int(y) / tilesizey
            if xx < 0 or xx >= sizex or yy < 0 or yy >= sizey:
                continue
            if sprite.name in self.matrix[yy][xx]:
                del self.matrix[yy][xx][sprite.name]

    def findCollisions(self, sprite):
        
        (sizex, sizey) = (self.data.width, self.data.height)
        (tilesizex, tilesizey) = (self.data.tilewidth, self.data.tileheight)
        collisions = {}
        candidates = {}

        # collect all of the nearby sprites
        for (x, y) in sprite.getPoints():
            xx, yy = int(x) / tilesizex, int(y) / tilesizey

            # off the edge?
            if xx < 0 or xx >= sizex or yy < 0 or yy >= sizey:
                collisions['boundary'] = True
                continue

            if self.data.solid[yy][xx]:
                collisions['solid'] = True

            for (name, other) in self.matrix[yy][xx].items():
                # sprites do not collide with themselves
                if other == sprite:
                    continue

                # add to the list of sprites to check against
                candidates[name] = other

        # now check for actual collisions with other nearby sprites
        for point in sprite.getPoints():
            added = []
            for (name, other) in candidates.items():
                if other.contains(point):
                    collisions[name] = other
                    added.append(name)

            for elt in added:
                del candidates[elt]

        for (name, other) in candidates.items():
            for point in other.getPoints():
                if sprite.contains(point):
                    collisions[name] = other

        return collisions

    def game_logic(self, keys, newkeys):
        # pass the heartbeat along to all the sprites
        for sprite in self.sprites.values():
            sprite.game_logic(keys, newkeys)

    def paint(self, surface):
        
        # blank the screen
        bg = pygame.Color(self.data.backgroundcolor)
        surface.fill(bg)

        # size of a single tile
        (tilesizex, tilesizey) = (self.data.tilewidth, self.data.tileheight)

        # position (in tiles) on the map of the top-left corner
        (corner_x, corner_y) = (self.x / tilesizex, self.y / tilesizey)

        # how far off (in pixels) we are from an even tile boundary
        (offset_x, offset_y) = (self.x % tilesizex, self.y % tilesizey)

        # how big is the view
        viewsize_x = (surface.get_width() + tilesizex - 1) / tilesizex
        viewsize_y = (surface.get_height() + tilesizey - 1) / tilesizey

        # gather list of sprites that might be visible
        sprites = {}

        for screen_y in range(viewsize_y + 1):
            map_y = screen_y + corner_y
            for screen_x in range(viewsize_x + 1):
                map_x = screen_x + corner_x

                # paint the background tile at this position
                if map_x < 0 or map_x >= self.data.width or map_y < 0 or map_y >= self.data.height:
                    continue

                gid = self.data.background[map_y][map_x]
                if gid > 0:
                    tile = self.data.tiles[gid]
                    surface.blit(tile,
                            (screen_x * tilesizex - offset_x,
                             screen_y * tilesizey - offset_y))

                # make note of any sprites that overlap this position
                sprites.update(self.matrix[map_y][map_x])

        # now paint any visible sprites
        for sprite in sprites.values():
            sprite.paint(surface)

        for screen_y in range(viewsize_y + 1):
            map_y = screen_y + corner_y
            for screen_x in range(viewsize_x + 1):
                map_x = screen_x + corner_x

                # paint the background tile at this position
                if map_x < 0 or map_x >= self.data.width or map_y < 0 or map_y >= self.data.height:
                    continue

                gid = self.data.foreground[map_y][map_x]
                if gid > 0:
                    tile = self.data.tiles[gid]
                    surface.blit(tile,
                            (screen_x * tilesizex - offset_x,
                             screen_y * tilesizey - offset_y))

                # make note of any sprites that overlap this position
                sprites.update(self.matrix[map_y][map_x])
