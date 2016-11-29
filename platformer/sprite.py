import math

class Sprite:
    def __init__(self, world, kind, name, width, height, x, y, maxspeed):
        self.world = world
        self.kind = kind
        self.name = name
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.maxspeed = maxspeed
        self.dx = 0.0
        self.dy = 0.0
        self.forces = {}

    # add a new force acting on this sprite
    # kind is one of: 'constant', 'onetime', 'slowdown'
    #   * constant forces are applied every frame
    #   * onetime forces are deleted after a single use
    #   * slowdown forces always push against the current direction,
    #     but never enough to change directions

    def addForce(self, name, vector, kind):
        self.forces[name] = (kind, vector)

    def removeForce(self, name):
        if name in self.forces:
            del self.forces[name]

    # get a list of points that make up the boundaries of this sprite
    # for collision detection purposes
    def getPoints(self):
        return [ (self.x,              self.y),
                 (self.x+self.width-1, self.y),
                 (self.x,              self.y+self.height-1),
                 (self.x+self.width-1, self.y+self.height-1) ]

    def contains(self, point):
        (x, y) = point
        return x >= self.x and \
               x < self.x+self.width and \
               y >= self.y and \
               y < self.y+self.height

    def move(self):
        if self.world is None:
            return

        # remove ourself from the collision matrix
        self.world.removeFromCollisionMatrix(self)

        # apply forces
        (dx, dy) = (self.dx, self.dy)
        for name in self.forces.keys():
            kind, (ddx, ddy) = self.forces[name]

            # cancel one-time forces after using them
            if kind == 'onetime':
                del self.forces[name]

            # apply the force
            if kind in ('constant', 'onetime'):
                dx += ddx
                dy += ddy
            elif kind == 'slowdown':
                dx -= math.copysign(min(abs(dx), abs(ddx)), self.dx)
                dy -= math.copysign(min(abs(dy), abs(ddy)), self.dy)

        # clip velocity to maximum speed in each direction
        (maxdx, maxdy) = self.maxspeed
        if abs(dx) > maxdx:
            dx = math.copysign(maxdx, dx)
        if abs(dy) > maxdy:
            dy = math.copysign(maxdy, dy)

        # apply the motion one step at a time and check for collisions
        movex = int(round(dx))
        movey = int(round(dy))

        while movex != 0 or movey != 0:
            if movex != 0:
                stepx = int(math.copysign(1, movex))
                old = self.x
                self.x += stepx
                for (name, other) in self.world.findCollisions(self).items():
                    stop = self.handleCollisionWith(name, other)
                    if stop:
                        # ran into something, so stop moving in x direction
                        stepx = 0
                        movex = 0
                        dx = 0.0
                        self.x = old
                movex -= stepx
            if movey != 0:
                stepy = int(math.copysign(1, movey))
                old = self.y
                self.y += stepy
                for (name, other) in self.world.findCollisions(self).items():
                    stop = self.handleCollisionWith(name, other)
                    if stop:
                        # ran into something, so stop moving in y direction
                        stepy = 0
                        movey = 0
                        dy = 0.0
                        self.y = old
                movey -= stepy

        (self.dx, self.dy) = (dx, dy)

        # update our position in the collision matrix
        self.world.addToCollisionMatrix(self)

    def paint(self, surface):
        raise NotImplementedError()

    def paintTile(self, surface, tile):
        (offsetx, offsety) = (self.world.x, self.world.y)
        surface.blit(tile, (self.x - offsetx, self.y - offsety))

    def game_logic(self, keys, newkeys):
        raise NotImplementedError()

    def handleCollisionWith(self, name, other):
        # default behavior: stop when you run into something
        return name == 'boundary' or name == 'solid'
