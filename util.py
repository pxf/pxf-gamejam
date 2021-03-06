#!/usr/bin/env python
import pygame.mixer
import pygame
import animatedsprite
#import os.path

class vec2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __repr__(self):
        return "vec2(" + str(self.x) + ", " + str(self.y) + ")"

    def get(self):
        return (self.x, self.y)

    def set(self, x, y):
        self.x = x
        self.y = y


def load_sound(name):
    if pygame.mixer.get_init == None:
        print 'Mixer is not initialized, load aborted.'
        return None
    try:
        sound = pygame.mixer.Sound(name)
        #sound = pygame.mixer.music.load(name)
    except pygame.error, message:
        print 'Cannot load sound'
        raise message
    return sound

cache = {} # has to be global (or a class variable)
def get_sequence(frames_names, sequence):
    frames = []
    global cache
    for name in frames_names:
        if not cache.has_key(name): # check if it has benn loaded already
            image = pygame.image.load(name) # not optimized
            cache[name] = image

        # constructs a sequence of frames equal to frames_names
        frames.append(cache[name])
    frames2 = []
    for idx in sequence:
        # constructing the animation sequence according to sequence
        frames2.append(frames[idx])
    return frames2

def name_sequence(basename, ext, num, num_digits=1, offset=0):
    names = []
    # format string basename+zero_padded_number+.+ext
    format = "%s%0"+str(num_digits)+"d.%s"
    for i in range(offset, num+1):
        new_name = format % (basename,i,ext)
        names.append(new_name)
    return names

def load_image(filename):
    image = pygame.image.load(filename)
    return image

def to_sprite(image):
    sprite = pygame.sprite.Sprite()
    sprite.image = image
    sprite.rect = image.get_rect()
    return sprite
"""
def load_sprite(filename):
    global cache
    if not cache.has_key(filename): # check if it has benn loaded already
        image = pygame.image.load(filename) # not optimized
        cache[filename] = image
    else:
        image = cache[filename]

    sprite = pygame.sprite.Sprite()
    sprite.image = image
    sprite.rect = image.get_rect().copy()
    return sprite
"""
