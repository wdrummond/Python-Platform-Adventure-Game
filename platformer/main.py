import game
import coin
import player
import mapfile
import world
import pygame
import badguy
import magic

class Platformer(game.Game):
    def __init__(self, name, map_filename, width, height, frames_per_second):
        game.Game.__init__(self, name, width, height, frames_per_second)
        pygame.mixer.init()
        

        # parse the map data
        data = mapfile.MapFile(map_filename)

        # create the world
        self.world = world.World(data)

        # create the sprites
        for elt in data.objects:
            # is this the player?
            if elt.kind == 'player':
                self.p = player.Player(self.world, elt)
                self.world.addSprite(self.p)

                # the world revolves around the player
                self.world.x = self.p.x + self.p.width / 2 - width / 2
                self.world.y = self.p.y + self.p.height / 2 - height / 2

            # is this a coin?
            elif elt.kind == 'coin':
                c = coin.Coin(self.world, elt)
                self.world.addSprite(c)

            elif elt.kind == 'badguy':
                b = badguy.BadGuy(self.world, elt)
                self.world.addSprite(b)

            elif elt.kind == "magic":
                    self.m = magic.Magic(self.world, elt)
                    

            else:
                print 'Sprite of unknown type {} found'.format(elt.kind)

        #score counter
        self.score_color = (255, 255, 255)
        self.score_x = 10
        self.score_y = 30
        self.coincount = 0
        self.font2 = pygame.font.SysFont("Courier New",20)


    def draw(self, surface):
        # rect = pygame.Rect(0,0,self.width,self.height)
        # surface.fill((0,0,0),rect )
        score_str = "Score: " + str(self.p.coincount)
        self.drawTextLeft(surface, score_str, self.score_color, self.score_x, self.score_y, self.font2)

    def drawTextLeft(self, surface, text, color, x, y,font):
        textobj = font.render(text, False, color)
        textrect = textobj.get_rect()
        textrect.bottomleft = (x, y)
        surface.blit(textobj, textrect)
        return

    def game_logic(self, keys, newkeys, buttons, newbuttons, mouse_position, dt):
        self.world.game_logic(keys, newkeys)
        if pygame.K_SPACE in newkeys:
            if self.p.face == 'right':
                self.world.addSprite(self.m)
                self.m.setx(self.p.x)
                self.m.sety(self.p.y)
            if self.p.face == 'left':
                self.world.addSprite(self.m)
                


    def paint(self, surface):
        # self.draw(surface)
        self.world.paint(surface)
        self.draw(surface)
       

def main():
    maplist = ['map.tmx', 'simplemap.tmx']
    g = Platformer('Dungeon Trainee!', maplist[0], 480, 480, 30)
    g.main_loop()

main()
