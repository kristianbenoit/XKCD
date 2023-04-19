#!/usr/bin/python3
# This software is licenced under a Creative Commons Attribution-NonCommercial 2.5 License. (just like xkcd)
# http://creativecommons.org/licenses/by-nc/2.5/

import sys
import io
import screeninfo
import pygame
import json
import xkcd
# Python 3
from urllib.request import urlopen
from urllib.error import HTTPError

# Python 2
#from urllib2 import Request
#from urllib2 import HTTPError

screenRatio=0.9

class xkcd_interface:
    def __init__(self):
        self.background_color = (255, 255, 255)
        pygame.init()
        pygame.mixer.quit()
        # Before using screeninfo I used this, but I cannot get info for indivudual monitor yet.
        #self.screenSize = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        monitor = screeninfo.get_monitors()[0]
        self.screenSize = (monitor.width, monitor.height)
        self.screen = pygame.display.set_mode(self.screenSize, pygame.FULLSCREEN)
        self.history = []

    def __loadImage(self, img, screenSize):
        img = pygame.image.load(img).convert(24)
        scaleFactor = 1
        if img.get_width() > screenSize[0] * screenRatio or img.get_height() > screenSize[1] * screenRatio :
            scaleFactor = min(float(screenRatio*screenSize[0])/img.get_width(), float(screenRatio*screenSize[1])/img.get_height())
        return pygame.transform.smoothscale(img, (int(scaleFactor*img.get_width()), int(scaleFactor*img.get_height())))

    @staticmethod
    def big_img(img_url):
        protocol, img_url = img_url.split('://', 1)
        protocol += '://'
        img_url = img_url.split('/')
        img_url[-1] = ''.join(img_url[-1].split('.')[:-1] + ["_2x."] + img_url[-1].split('.')[-1:])
        return protocol + '/'.join(img_url)

    def showImage(self, img_id = ''):
        try:
            json_data = json.loads(urlopen('https://xkcd.com/' + str(img_id) + '/info.0.json').read())
        except HTTPError:
            self.showImage()
            return
        print('Showing image of %(year)s/%(month)s/%(day)s (%(num)s)' % json_data)
        try: # To show the 2x image if possible
            img = self.__loadImage(io.BytesIO(urlopen(xkcd_interface.big_img(json_data['img'])).read()), self.screenSize)
        except HTTPError:
            img = self.__loadImage(io.BytesIO(urlopen(json_data['img']).read()), self.screenSize)
        self.history += [json_data['num']]
        self.screen.fill(self.background_color)
        self.screen.blit(img, ((self.screenSize[0] - img.get_width())/2, (self.screenSize[1] - img.get_height())/2))
        pygame.display.flip()

xkcd = xkcd_interface()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isnumeric():
        xkcd.showImage(sys.argv[1])
    else:
        xkcd.showImage()
    # This is an animated gif. Which does not work with pygame.
    #xkcd.showImage(961) 
    # I should use PIL and Tkinter to show the image.
    # https://stackoverflow.com/questions/7960600/python-tkinter-display-animated-gif-using-pil
    # foung by:
    # https://stackoverflow.com/questions/1412529/how-do-i-programmatically-check-whether-a-gif-image-is-animated
    while True:
        #print(xkcd.history)
        event = pygame.event.wait()
        # Enhancement Ideas:
        # 1 - navigate the history with 'p' and 'n'
        # 2 - support dead keys including 'gg', '35j', '5k', '5p', '5n'.
        # 3 - Capital letters i.e. 'G'.
        # 4 - Support accessing a random comic with '.'.
        # 5 - go forward and back a year with 'Ctrl-f' and 'Ctrl-b'.
        # 6 - Go to first slide with 'gg'.
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_j, pygame.K_DOWN, pygame.K_LEFT]:
            # Previous
            xkcd.showImage(xkcd.history[-1] - 1)
            continue
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_k, pygame.K_UP, pygame.K_RIGHT]:
            # Next
            xkcd.showImage(xkcd.history[-1] + 1) 
            continue
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_HOME]:
            # First
            xkcd.showImage(1)
            continue
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_END]:
            # Last
            xkcd.showImage()
            continue
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_PAGEDOWN]:
            # Go back a year.
            img_nb = xkcd.history[-1]
            if img_nb - 156 > 0:
                img_nb = img_nb - 156
            xkcd.showImage(img_nb)
            continue
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_PAGEUP]:
            # Go ahead a year.
            img_nb = xkcd.history[-1]
            img_nb = img_nb + 156
            xkcd.showImage(img_nb)
            continue
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_q]:
            # Quit
            break

    pygame.display.quit()
