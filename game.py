import sys, pygame
from pygame.locals import *

import player
import stage
import gameobject
import util
import camera
import animation
import billboard

import pymunk as pm
# lol enums
CNONE,CRED,CBLUE,CGREEN = range(4)
PDIR_RIGHT,PDIR_LEFT = range(2)

vel_epsilon = 0.1

class Game:
    def init_physics(self):
        pm.init_pymunk()
        self.space = pm.Space() #3
        self.space.gravity = (0.0, 300.0)
        self.space.resize_static_hash()
        self.space.resize_active_hash()

        # collisions between different colors
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_RED, gameobject.OBJECT_TYPE_GREEN, None)
        #self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_GREEN, gameobject.OBJECT_TYPE_RED, None)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_GREEN, gameobject.OBJECT_TYPE_BLUE, None)
        #self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_BLUE, gameobject.OBJECT_TYPE_GREEN, None)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_RED, gameobject.OBJECT_TYPE_BLUE, None)
        #self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_BLUE, gameobject.OBJECT_TYPE_RED, None)

        # key collisions
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_KEY_RED, self.handle_key_collisions, self.screen)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_KEY_GREEN, self.handle_key_collisions, self.screen)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_KEY_BLUE, self.handle_key_collisions, self.screen)

        # win collisions
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_GOAL, self.handle_win_collisions, self.screen)

        # info collisions
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_INFO, self.handle_info_collisions, self.screen)

        # collisions between
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_RED, self.handle_collision, self.screen)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_GREEN, self.handle_collision, self.screen)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_BLUE, self.handle_collision, self.screen)
        self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_BW, self.handle_collision, self.screen)
        #self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_RED, gameobject.OBJECT_TYPE_PLAYER, self.handle_collision, self.screen)
        #self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_GREEN, gameobject.OBJECT_TYPE_PLAYER, self.handle_collision, self.screen)
        #self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_BLUE, gameobject.OBJECT_TYPE_PLAYER, self.handle_collision, self.screen)

    def __init__(self, size, scale):
        pygame.init()
        self.scale = scale
        self.size = size
        if scale:
            self.window = pygame.display.set_mode((size[0]*2, size[1]*2))
        else:
            self.window = pygame.display.set_mode(size)

        self.screen = pygame.Surface(size)
        self.screen.set_colorkey((0,0,0))
        self.actual_screen = pygame.display.get_surface()
        self.camera = camera.Camera(util.vec2(30,25),size)

        pygame.mouse.set_visible(0)
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.restart_level_counter = -1
        self.current_stage_id = stage.STAGE_INTRO
        self.remove_player = False

        # physics
        #init_physics()


        # music:
        self.bg_music = util.load_sound("data/channel_panic!-theme.ogg")
        #self.bg_music.play(-1)
        #self.bg_music_playing = True
        self.bg_music_playing = False
        # billboards
        self.billboards = []
        self.billboards.append(billboard.Billboard("data/background_stars.png",util.vec2(0,0),10,True))
        self.billboards.append(billboard.Billboard("data/background_city.png",util.vec2(0,210),40,True,False,False))
        self.billboards.append(billboard.Billboard("data/background_city2.png",util.vec2(0,190),30,True,False,True))

        #timer
        self.map_timer = billboard.GuiTimerBar(util.vec2(240,0),15)

        # misc
        names = util.name_sequence("data/entity_door","png",4)
        # lol hack
        frames = util.get_sequence(names,[0,1,2,3,4,4,4,4,4,4,4,4,4,4])
        self.door_anim = animation.Animation(frames,8)
        self.animate_door = False

        self.fade_in_out = False
        self.fade_in_out_time = 0

        self.playing_intro = True

        # key gui thingy
        self.gui_key = billboard.GuiKeys(util.vec2(0,0),16)

        # game settings
        #self.player = player.Player(util.vec2(100,20), self.space)
        #print(self.player.object_type)
        #self.camera = camera.Camera(util.vec2(30,25),size)
        #self.current_stage = None
        # set color key to black
        #self.screen.set_colorkey(pygame.Color(0,0,0))
        pygame.key.set_repeat(1, 20)

        #self.active_color = CRED

    def create_splosions(self, spltype):
        for i in range(30):
            splobj = gameobject.SplosionBlock(util.vec2(self.player.body.position.x, self.player.body.position.y), self.space, spltype)
            self.current_stage.splosion_objects.append(splobj)

    def handle_key_collisions(self, shapea, shapeb, contacts, normal_coef, surface):
        if (shapea.collision_type == gameobject.OBJECT_TYPE_KEY_RED or shapeb.collision_type == gameobject.OBJECT_TYPE_KEY_RED):
            self.current_stage.keys[gameobject.OBJECT_TYPE_KEY_RED] = True
            self.gui_key.update(gameobject.OBJECT_TYPE_KEY_RED)

        elif (shapea.collision_type == gameobject.OBJECT_TYPE_KEY_GREEN or shapeb.collision_type == gameobject.OBJECT_TYPE_KEY_GREEN):
            self.current_stage.keys[gameobject.OBJECT_TYPE_KEY_GREEN] = True
            self.gui_key.update(gameobject.OBJECT_TYPE_KEY_GREEN)

        elif (shapea.collision_type == gameobject.OBJECT_TYPE_KEY_BLUE or shapeb.collision_type == gameobject.OBJECT_TYPE_KEY_BLUE):
            self.current_stage.keys[gameobject.OBJECT_TYPE_KEY_BLUE] = True
            self.gui_key.update(gameobject.OBJECT_TYPE_KEY_BLUE)

        if (shapea.collision_type == gameobject.OBJECT_TYPE_PLAYER):
            shapeb.body.position = (-10000,-10000)
        else:
            shapea.body.position = (-10000,-10000)

        return False

    def handle_info_collisions(self, shapea, shapeb, contacts, normal_coef, surface):
        # find correct info block
        for infoblock in self.current_stage.info_blocks:
            if (infoblock.shape == shapea or infoblock.shape == shapeb):
                infoblock.activate()

        return False

    def handle_win_collisions(self, shapea, shapeb, contacts, normal_coef, surface):
        if self.current_stage.finished():
            if not self.door_anim.playing:
                self.door_anim.play()
            self.animate_door = True
        return False

    def handle_collision(self, shapea, shapeb, contacts, normal_coef, surface):
        import math
        #self.player.in_air = False
        for c in contacts:

            """if (shapea.collision_type == gameobject.OBJECT_TYPE_RED and shapeb.collision_type == gameobject.OBJECT_TYPE_RED):
                return True
            elif (shapea.collision_type == gameobject.OBJECT_TYPE_GREEN and shapeb.collision_type == gameobject.OBJECT_TYPE_GREEN):
                return True
            elif (shapea.collision_type == gameobject.OBJECT_TYPE_BLUE and shapeb.collision_type == gameobject.OBJECT_TYPE_BLUE):
                return True"""

            cs = [shapea.collision_type, shapeb.collision_type]
            alles = [gameobject.OBJECT_TYPE_RED
                    ,gameobject.OBJECT_TYPE_GREEN
                    ,gameobject.OBJECT_TYPE_BLUE]

            m = {CRED: gameobject.OBJECT_TYPE_RED
                ,CGREEN: gameobject.OBJECT_TYPE_GREEN
                ,CBLUE: gameobject.OBJECT_TYPE_BLUE}

            in_air = True
            r = max( 3, abs(c.distance*5) )
            spawn_splosions = False
            if (r > 24.0):
                spawn_splosions = True
            if (c.normal.y > 0 and c.normal.x < 0.1 and c.normal.x > -0.1):
                in_air = False

            self.player.is_pushing = False
            if all(x not in alles for x in cs) or m[self.player.active_color] in cs:# or any(not hasattr(x, 'is_movable') for x in cs):
                if (c.position.y - self.player.body.position.y < 1):
                    for dyn_obj in self.current_stage.game_objects:
                        if (dyn_obj.shape == shapea or dyn_obj.shape == shapeb):
                            self.player.is_pushing = True
                            #print("moving: ", c.position.y - self.player.body.position.y)

                if math.fabs(self.player.body.position.y - c.position.y) == 0.0:
                    d = c.position.x - self.player.body.position.x
                    if d < 0:
                        self.player.body.position.x += 0.3
                    else:
                        self.player.body.position.x -= 0.3

            if (shapea.collision_type == gameobject.OBJECT_TYPE_BW or shapeb.collision_type == gameobject.OBJECT_TYPE_BW):
                self.player.in_air = in_air
                return True;


            if (self.active_color == CRED):
                if (shapea.collision_type == gameobject.OBJECT_TYPE_RED or shapeb.collision_type == gameobject.OBJECT_TYPE_RED):
                    if (spawn_splosions):
                        self.create_splosions(gameobject.OBJECT_TYPE_RED)
                        self.restart_level_counter = 4.0
                        self.remove_player = True
                    self.player.in_air = in_air
                    return True;
            elif (self.active_color == CGREEN):
                if (shapea.collision_type == gameobject.OBJECT_TYPE_GREEN or shapeb.collision_type == gameobject.OBJECT_TYPE_GREEN):
                    if (spawn_splosions):
                        self.create_splosions(gameobject.OBJECT_TYPE_GREEN)
                        self.restart_level_counter = 4.0
                        self.remove_player = True
                    self.player.in_air = in_air
                    return True;
            elif (self.active_color == CBLUE):
                if (shapea.collision_type == gameobject.OBJECT_TYPE_BLUE or shapeb.collision_type == gameobject.OBJECT_TYPE_BLUE):
                    if (spawn_splosions):
                        self.create_splosions(gameobject.OBJECT_TYPE_BLUE)
                        self.restart_level_counter = 4.0
                        self.remove_player = True
                    self.player.in_air = in_air
                    return True;

        return False

    def update_title(self):
        pygame.display.set_caption("Channel Panic! (%.2f FPS)" % (self.clock.get_fps()))

    def check_timer(self):
        if self.map_timer.has_stopped:
            if self.player.active_color == CRED:
                self.create_splosions(gameobject.OBJECT_TYPE_RED)
            if self.player.active_color == CGREEN:
                self.create_splosions(gameobject.OBJECT_TYPE_GREEN)
            if self.player.active_color == CBLUE:
                self.create_splosions(gameobject.OBJECT_TYPE_BLUE)
            self.restart_level_counter = 4.0
            self.remove_player = True
            self.map_timer.reset(4.0)

    def start_new_level(self, stage_id):
        self.current_stage_id = stage_id

        self.restart_level_counter = -1
        self.init_physics()
        self.remove_player = False

        self.player = player.Player(util.vec2(100,20), self.space)
        self.active_color = self.player.toggle_color(CRED)

        self.gui_key.reset()

        stages = {
            stage.STAGE_INTRO: stage.StageIntro,
            stage.STAGE_0: stage.Stage0,
            stage.STAGE_1: stage.Stage1,
            stage.STAGE_2: stage.Stage2,
            stage.STAGE_4: stage.Stage4,
            stage.STAGE_3: stage.Stage3,
            stage.STAGE_5: stage.Stage5,
            stage.STAGE_6: stage.Stage6,
            stage.STAGE_7: stage.Stage7,
            stage.STAGE_8: stage.Stage8,
            stage.STAGE_9: stage.Stage9,
            stage.STAGE_10: stage.Stage10,
            stage.STAGE_11: stage.Stage11
        }

        if not self.current_stage_id == stage.STAGE_INTRO:
            self.map_timer.reset()
            self.map_timer.show()
        else:
            self.map_timer.hide()

        if stage_id > len(stages)-1:
            stage_id = 0
            self.current_stage_id = 0

        self.set_level(stages[stage_id](self.camera, self.player, self.space))

    def set_level(self, stage):
        self.current_stage = stage
        self.map_timer.map_time = stage.map_time

    def handle_input(self, event):
        if event.type == KEYUP and event.key in (K_LEFT, K_RIGHT):
            self.player.stop_hammer_time = True

        #switch colors
        if event.key == K_1:
            self.active_color = self.player.toggle_color(CRED)
        if event.key == K_2:
            self.active_color = self.player.toggle_color(CGREEN)
        if event.key == K_3:
            self.active_color = self.player.toggle_color(CBLUE)

        if event.type == KEYUP:
            if event.key == K_r:
                self.start_new_level(self.current_stage_id)
            if event.key == K_l:
                self.start_new_level(self.current_stage_id+1)

    def game_input(self):
        if pygame.key.get_pressed()[K_UP]:
            #self.player.vel.y = -3
            #self.in_air = True
            if (not self.player.in_air):
                self.player.body.apply_impulse((0,-1080))
            pass

        if pygame.key.get_pressed()[K_LEFT]:
                self.player.stop_hammer_time = False
            #if (len(self.physics.get_colliding_objects(self.physics.player)) > 0):

                #if (-self.player.body._get_velocity().x < 80.0):
                if (self.player.in_air):
                    self.player.body.apply_impulse((-50,0))
                else:
                    self.player.body.apply_impulse((-100,0))

                self.player.look_dir = PDIR_LEFT

                #self.player.look_dir = 1
                self.player.has_changed = True
                #self.player.vel.y = 0.04

        if pygame.key.get_pressed()[K_RIGHT]:
                self.player.stop_hammer_time = False
            #if (len(self.physics.get_colliding_objects(self.physics.player)) > 0)
                if (self.player.in_air):
                    self.player.body.apply_impulse((50,0))
                else:
                    self.player.body.apply_impulse((100,0)) #_set_velocity((-80, 0))
                self.player.has_changed = True
                self.player.look_dir = PDIR_RIGHT
                #self.player.vel.x += 0.9
                #self.player.vel.y = 0.04

        if pygame.key.get_pressed()[K_F1]:
            if self.bg_music_playing:
                self.bg_music.stop()
                self.bg_music_playing = False
            else:
                self.bg_music.play(1)
                self.bg_music_playing = True

        if pygame.key.get_pressed()[K_ESCAPE]:
            self.is_running = False


    def run(self):

        pxf_logo = animation.new_animation("data/pxf_logo0", "png", 12, 5, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12][:-1])
        pxf_logo.play()
        intro_end_time = 5000
        while self.playing_intro:
            self.dt_last_frame = self.clock.tick(60)
            intro_end_time -= self.dt_last_frame
            if intro_end_time <= 0:
                self.playing_intro = False

            self.screen.fill([0,0,0])

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.playing_intro = False
                    self.is_running = False
                if event.type == pygame.KEYUP:
                    if (event.key == K_ESCAPE):
                        self.playing_intro = False



            pxf_logo.update(self.dt_last_frame)
            pxf_logo.draw(self.screen, (self.size[0] / 2 - 64, self.size[1] / 2 - 64), True)

            if self.scale:
                pygame.transform.scale2x(self.screen, self.actual_screen)
            else:
                self.actual_screen.blit(self.screen, (0, 0))

            pygame.display.flip()



        #self.set_level(stage.Stage1(self.camera, self.player, self.space))
        self.start_new_level(self.current_stage_id)

        while self.is_running:
            # update time
            self.dt_last_frame = self.clock.tick(60)

            if (self.restart_level_counter > 0):
                self.player.body.position = (-111111, -111111)
                self.restart_level_counter -= self.dt_last_frame / 1000.0
                if (self.restart_level_counter <= 0):
                    self.start_new_level(self.current_stage_id)

            # event handling
            if (self.restart_level_counter < 0):
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.is_running = False
                    elif event.type in (KEYDOWN, KEYUP):
                        self.handle_input(event)

                # handle game input
                self.game_input()

            self.screen.fill([0,0,0])

            # update animation
            #self.anim_test.update(self.dt_last_frame)
            #self.anim_test.draw(self.screen)

            # update player
            self.player.update(self.camera.get_pos(),self.dt_last_frame)

            # update physics
            self.space.step(1/60.0)
            if (self.remove_player):
                self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_RED, None)
                self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_GREEN, None)
                self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_BLUE, None)
                self.space.add_collisionpair_func(gameobject.OBJECT_TYPE_PLAYER, gameobject.OBJECT_TYPE_BW, None)
                self.remove_player = False

            # update game objects
            for object in self.current_stage.tiles:
                #object.update(self.camera.pos)
                object.update(self.camera.get_pos())

            for splosion in self.current_stage.splosion_objects:
                splosion.update(self.camera.get_pos())

            for obj in self.current_stage.game_objects:
                obj.update(self.camera.get_pos())

            for inf in self.current_stage.info_blocks:
                inf.update(self.camera.get_pos(),self.dt_last_frame)

            # update camera
            if (self.restart_level_counter < 0):
                self.camera.set_lookat(util.vec2(self.player.body.position.x, self.player.body.position.y))
            self.camera.update()

            # draw billboards
            for billboard in self.billboards:
                billboard.update(self.camera.get_pos(),self.dt_last_frame)
                billboard.draw(self.screen)

            # update game
            self.current_stage.draw(self.screen)

            if self.animate_door:
                self.door_anim.update(self.dt_last_frame)
                p = self.current_stage.doorpos
                p = (p[0] - self.camera.get_pos().x, p[1] - self.camera.get_pos().y)
                self.door_anim.draw(self.screen, p, True)
                if self.door_anim.current == len(self.door_anim.frames)-1:
                    self.start_new_level(self.current_stage_id + 1)
                    self.door_anim.current = 0
                    self.animate_door = False
                    self.door_anim.stop()
                elif self.door_anim.current == 3:
                    self.fade_in_out = True
                    self.fade_in_out_time = 3


            self.player.draw(self.screen)

            # draw key gui
            self.gui_key.draw(self.screen)

            self.map_timer.update(self.dt_last_frame)
            self.map_timer.draw(self.screen)

            self.check_timer()

            if self.fade_in_out:
                self.fade_in_out_time -= self.dt_last_frame / 1000.0
                surf = pygame.Surface(self.size)
                surf.fill((0, 0, 0))
                if self.fade_in_out_time > 2.0:
                    a = 255 - int(255 * ((self.fade_in_out_time-2.0)/2.0))
                else:
                    a = int(255 * ((self.fade_in_out_time)/1.0))
                surf.set_alpha(a)
                self.screen.blit(surf, (0, 0))
                if self.fade_in_out_time <= 0.0:
                    self.fade_in_out = False

            # fps limit
            #3self.clock.tick(25)
            self.update_title()

            if self.scale:
                pygame.transform.scale2x(self.screen, self.actual_screen)
            else:
                self.actual_screen.blit(self.screen, (0, 0))

            # swap buffers
            pygame.display.flip()

if __name__ == '__main__':
    g = Game((320, 240), True)
    g.run()
