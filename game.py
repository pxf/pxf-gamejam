import sys, pygame
from pygame.locals import *

import player
import stage
import gameobject
import util
import camera
import physics

class Game:
    def __init__(self, size):
        pygame.init()
        self.window = pygame.display.set_mode(size)
        self.screen = pygame.display.get_surface()
        pygame.mouse.set_visible(0)
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.bg_music = util.load_sound("data/channel_panic!-theme.ogg")
        self.bg_music_playing = False
        self.player = player.Player(util.vec2(4,25))
        self.camera = camera.Camera(self.player.pos,size)
        self.current_stage = None
        self.physics = physics.Physics()
        # set color key to black
        self.screen.set_colorkey(pygame.Color(0,0,0))

    def update_title(self):
        pygame.display.set_caption("Channel Panic! (%.2f FPS)" % (self.clock.get_fps()))

    def set_level(self, stage):
        self.physics.reset()
        self.current_stage = stage

        for o in self.current_stage.game_objects:
            self.physics.add_dynamic(o)

        for o in self.current_stage.tiles:
            self.physics.add_static(o)

        self.physics.add_dynamic(self.player)

    def handle_input(self, event):
        if event.key == K_UP:
            self.camera.pos = self.camera.pos + util.vec2(1,0)
            pass

        if event.key == K_LEFT:
            self.player.look_dir = 1
            self.player.pos.x -= 1.0

        if event.key == K_RIGHT:
            self.player.look_dir = 0
            self.player.pos.x += 1.0

            #pass
        if event.key == K_SPACE:
            if not self.bg_music_playing:
                self.bg_music.play(1)
                self.bg_music_playing = True
            else:
                self.bg_music.stop()
                self.bg_music_playing = False
        if event.key == K_ESCAPE:
            self.is_running = False

    def run(self):
        self.set_level(stage.Stage1(self.camera))

        while self.is_running:
            # event handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.is_running = False
                elif event.type == KEYDOWN:
                    self.handle_input(event)

            self.screen.fill([0,0,0])

            # update player
            self.player.update()
            self.player.draw(self.screen)

            # update game objects
            for object in self.current_stage.tiles:
                #object.update(self.camera.pos)
                object.update(util.vec2(0, 0))

            # update camera
            self.camera.update()

            # update physics
            self.physics.step()

            # update game
            self.current_stage.draw(self.screen)

            # fps limit
            self.clock.tick(25)
            self.update_title()
            # swap buffers
            pygame.display.flip()

if __name__ == '__main__':
    g = Game((320, 240))
    g.run()
