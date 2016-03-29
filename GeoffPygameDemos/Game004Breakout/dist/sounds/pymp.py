#!/usr/bin/env python

'''
PyMP (Pygame's Music Player)
by Takis Tsiberis
http://takira.freehosting.net/
takira_gr@yahoo.com

Copyright (C) 2006 Panagiotis Tsiberis
This program is free software;
you can redistribute it and/or
modify it under the terms of the
GNU General Public License
as published by the
Free Software Foundation;
either version 2 of the License,
or (at your option) any later version.
'''

#-------------------Imports-------------------
import pygame
from pygame.locals import *
from os import path, listdir, getcwd, chdir
from locale import getdefaultlocale

#-------------------Constants-------------------
VERSION = '0.1'
HOME_DIRECTORY = getcwd()
SIZE = (400, 200)
BARSIZE = 18
BARSIZE_2 = 48
XDIST = 3
GREY = (60,60,60)
BLUE = (100,150,200)
WHITE = (255,255,255)
BLACK = (0,0,0)
DEFAULTLOCALE = getdefaultlocale()
LDIST = 10
RANDOM_NUMBER = '7380851593990774798948024965297435647110'
H_B = SIZE[1]-BARSIZE*2-BARSIZE_2
BYR1 = BARSIZE + BARSIZE_2
BYR2 = SIZE[1] - BARSIZE
SURFH = SIZE[1] - BARSIZE*4
BB = BARSIZE + BARSIZE_2

#-------------------Globals-------------------
SAMPLING_RATE = 44100
SAMPLE_SIZE = 16
STEREO = 2
BUFFER_SIZE = 4096

#-------------------Classless functions-------------------
def load_image(name, colorkey=None):
    fullname = path.join(HOME_DIRECTORY+'\\data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def display_some_text(text,image,x,r=0,y=0,about=0):
    if not about:
        text_len = len(text)
        if text_len >= 22:
            size = 12
        else:
            size = 16
    else:
        size = 14
    if not r:
        Font = pygame.font.Font(path.join(HOME_DIRECTORY+'\\data','MgOpenCosmeticaBoldOblique.ttf'),size)
        if not about:
            font = Font.render(unitext(text), 1, WHITE)
        else:
            font = Font.render(unitext(text), 1, BLUE)
    else:
        Font = pygame.font.Font(path.join(HOME_DIRECTORY+'\\data','MgOpenCosmeticaRegular.ttf'),12)
        font = Font.render(unitext(text), 1, BLUE)
    if not y:
        h1 = image.get_height()
        h2 = font.get_height()
        h = (h1 - h2) / 2
        image.blit(font,(x,h))
    else:
        image.blit(font,(x,y))

def _print(display_image,text,name=''):
    display_image.fill(GREY)
    alltext = text + name
    for size in range(12,4,-1):
        Font = pygame.font.Font(path.join(HOME_DIRECTORY+'\\data','MgOpenCosmeticaRegular.ttf'),size)
        font = Font.render(unitext(alltext), 1, BLUE)
        if font.get_width() <= (display_image.get_width() - 11):
            break
    h1 = display_image.get_height()
    h2 = font.get_height()
    h = (h1 - h2) / 1
    display_image.blit(font,(10,h))

def unitext(text):
    # Thanks to Marc-Andre Lemburg
    utext = ''
    a = unicode(text,DEFAULTLOCALE[1])
    for char in a:
        c = ord(char)
        b = unichr(c)
        utext = utext + b
    return utext
    
def get_drives():
    drive_list = []
    number_of_drives = pygame.cdrom.get_count()
    for x in range(number_of_drives):
        drive = pygame.cdrom.CD(x)
        drive_name = drive.get_name()
        drive_list.append((x, drive_name))
    return drive_list

def quit_drives():
    for x in get_drives():
        if pygame.cdrom.CD(x[0]).get_init():
            pygame.cdrom.CD(x[0]).stop()
            pygame.cdrom.CD(x[0]).quit()

def find_drives():
    # By Nicolas Favre-Felix
    L = []
    for i in range(ord('a'), ord('z')+1):
        drive = chr(i).upper()+':\\'
        if path.exists(drive):
            L.append(drive)
    return L

def go_up(a):
    if path.ismount(a):
        return RANDOM_NUMBER
    else:
        b = path.split(a)[0]
        return b

def create_dirs(a):
    dirlist = []
    filelist = []
    _path_ = ''
    is_top = 0

    if a == RANDOM_NUMBER:
        dirlist = find_drives()
        _path_ = 'My Computer'
        is_top = 1
    else:
        chdir(a)
        b = listdir(a)

        for x in b:
            if not x[0] == '.':
                if path.isdir(x):
                    dirlist.append(x)
                elif path.isfile(x):
                    if x[-4:].upper() == '.WAV'\
                       or x[-4:].upper() == '.OGG'\
                       or x[-4:].upper() == '.MID'\
                       or x[-4:].upper() == '.CDA'\
                       or x[-3:].upper() == '.XM':
                        filelist.append(x)

        dirlist.sort()
        filelist.sort()

        if path.ismount(a):
            _path_ = a
        else:
            _path_ = path.split(a)[1]

    return (is_top, _path_, dirlist, filelist)

def play(song,statusimage):
    if song[-4:].upper() == '.WAV'\
        or song[-4:].upper() == '.OGG'\
        or song[-4:].upper() == '.MID'\
        or song[-3:].upper() == '.XM':

        quit_drives()

        try:
            pygame.mixer.music.load(song)
            _print(statusimage,'Just loaded... ',song)
            pygame.mixer.music.play()
        except RuntimeError:
            _print(statusimage,'Could not load... ',song)

    elif song[-4:].upper() == '.CDA':

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        drive_name, drive_tail = path.splitdrive(song)
        drive_name = drive_name + '\\'
        drive_tail = drive_tail[2:]

        for x in get_drives():
            if drive_name in x:
                drive_id = x[0]

        track_list = listdir(drive_name)
        track_num = track_list.index(drive_tail)

        v = pygame.cdrom.CD(drive_id)
        v.init()
        try:
            _print(statusimage,'Just loaded...',song)
            v.play(track_num)
        except RuntimeError:
            _print(statusimage,'Could not load...',song)

def slice_the_list(a,b):
    c = b.index(a)
    d1 = b[:c]
    d2 = b[(c+1):]
    return d1,d2

#-------------------Classes-------------------
class scroll_surface(pygame.sprite.Sprite):
    def __init__(self,_width,_height):
        pygame.sprite.Sprite.__init__(self)
        self._width = _width
        self._height = _height
        self.is_clicked = 0
        self.is_dirty = 1
        self.image = pygame.Surface((self._width,self._height)).convert()
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
    def update(self):
        pass
    def is_focused(self,(x,y)):
        return self.rect.collidepoint(x,y)

class scroll_pad(pygame.sprite.Sprite):
    def __init__(self,width,height):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width,self.height)).convert()
        if height == 128:
            self.image.fill(BLACK)
        else:
            self.image.fill(BLUE)
            self.image.lock()
            pygame.draw.line(self.image, WHITE, (0,0), (0,self.height))
            pygame.draw.line(self.image, WHITE, (0,0), (self.width,0))
            pygame.draw.line(self.image, BLACK, (0,self.height-1), (self.width,self.height-1))
            self.image.unlock()
        self.rect = self.image.get_rect()
        self.is_clicked = 0
    def is_focused(self,(x,y)):
        return self.rect.collidepoint(x,y)
    def update(self):
        pass
    def move(self,x,y):
        self.rect = self.rect.move(x, y)

class scroll_button(pygame.sprite.Sprite):
    image_list = None
    def __init__(self,rank,size,iss):
        pygame.sprite.Sprite.__init__(self)
        self.rank = rank
        self.size = size
        self.iss = iss
        if scroll_button.image_list is None:
            image0 = load_image('up_arrow.png',-1)
            image1 = load_image('down_arrow.png',-1)
            scroll_button.image_list = [image0, image1]
        self.image_list = scroll_button.image_list
        self.image = pygame.Surface((self.size,self.size)).convert()
        if self.iss:
            self.image.fill(BLUE)
        else:
            self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        arrow = self.image_list[self.rank]
        arrow_rect = arrow.get_rect()
        arrow_rect.center = self.rect.center
        self.image.blit(arrow,arrow_rect)
        self.is_clicked = 0
        self.is_dirty = 1
    def update(self):
        if self.iss:
            if self.is_clicked:
                self.image.lock()
                pygame.draw.line(self.image, BLUE, (0,0), (0,self.size))
                pygame.draw.line(self.image, WHITE, (self.size-1,0), (self.size-1,self.size))
                pygame.draw.line(self.image, BLACK, (0,0), (self.size,0))
                pygame.draw.line(self.image, WHITE, (0,self.size-1), (self.size,self.size-1))
                self.is_dirty = 1
                self.image.unlock()
            elif self.is_dirty:
                self.image.lock()
                pygame.draw.line(self.image, WHITE, (0,0), (0,self.size))
                pygame.draw.line(self.image, BLUE, (self.size-1,0), (self.size-1,self.size))
                pygame.draw.line(self.image, WHITE, (0,0), (self.size,0))
                pygame.draw.line(self.image, BLACK, (0,self.size-1), (self.size,self.size-1))
                self.is_dirty = 0
                self.image.unlock()
        else:
            pass
    def is_focused(self,(x,y)):
        return self.rect.collidepoint(x,y)

class scroll_bar:
    def __init__(self,bd,iss):
        # Make two scroll buttons
        a = scroll_button(0,BARSIZE,iss)
        b = scroll_button(1,BARSIZE,iss)
        a.rect.topleft = (SIZE[0] - BARSIZE - XDIST, BARSIZE)
        b.rect.bottomleft = (SIZE[0] - BARSIZE - XDIST, SIZE[1] - BARSIZE)
        # Make the scroll surface
        c = scroll_surface(BARSIZE, SURFH)
        c.rect.center = (a.rect.center[0], SIZE[1]/2)
        # Make a scroll pad
        if bd == 0 or bd <= H_B:
            self.pad_height = SURFH
        else:
            bd = bd * 1.0
            self.pad_height = int(round(SURFH / (bd/H_B)))
            if self.pad_height < 4: self.pad_height = 4
        d = scroll_pad(BARSIZE,self.pad_height)
        d.rect.topleft = (SIZE[0] - BARSIZE - XDIST, BARSIZE*2)
        # Initialize
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.group = [self.a, self.b, self.c, self.d]

        self.wi = self.d.width
        self.a1 = self.d.rect.topleft[0]
        self.a2 = self.d.rect.topleft[1]
        self.a3 = self.b.rect.topleft[0]
        self.a4 = self.b.rect.topleft[1]
        self.buttongroup = [self.a, self.b]
        self.scrollbarsprites = pygame.sprite.OrderedUpdates(self.group)
    def update(self):
        collide = pygame.sprite.spritecollide(self.d, self.buttongroup, False)
        if collide:
            self.d.__init__(self.wi,self.pad_height)
            self.d.is_clicked = 1
            if collide == [self.a]:
                self.d.rect.topleft = (self.a1,self.a2)
            elif collide == [self.b]:
                self.d.rect.bottomleft = (self.a3,self.a4)
        self.scrollbarsprites.update()

class dir_button(pygame.sprite.Sprite):
    image_list = None
    def __init__(self,rank,text=''):
        pygame.sprite.Sprite.__init__(self)
        if dir_button.image_list is None:
            image0 = load_image('stock_left.png',-1)
            image1 = load_image('stock_left_2.png',-1)
            image2 = load_image('gnome-fs-directory-visiting.png')
            image3 = load_image('gnome-fs-directory.png',-1)
            image4 = load_image('gnome-fs-regular.png',-1)
            dir_button.image_list = [image0, image1, image2, image3, image4]
        self.image1 = dir_button.image_list[rank]
        h1 = self.image1.get_height()
        w1 = self.image1.get_width()
        if rank in [0,1,2]:
            b = LDIST
        else:
            b = LDIST * 2
        image2 = pygame.Surface((SIZE[0]- BARSIZE - XDIST, h1)).convert()
        image2.fill(BLACK)
        image2.blit(self.image1,(b, 0))
        display_some_text(text, image2, b + w1 + LDIST)
        self.image = image2
        self.rect = self.image.get_rect()
        self.text = text
        self.is_clicked = 0
        self.ymax = 0
    def is_focused(self,(x,y)):
        return self.rect.collidepoint(x,y)

class folder_bar:
    def __init__(self):
        self.image = pygame.Surface((SIZE[0]- BARSIZE - XDIST, BARSIZE_2)).convert()
        self.image.fill(BLACK)
        self.image2 = pygame.Surface((SIZE[0]- BARSIZE - XDIST, BARSIZE_2)).convert()
        self.image2.fill(BLACK)
    def write_to(self,a,b):
        self.folderbarlist = []
        self.a = a
        self.b = b
        d1 = dir_button(a)
        d2 = dir_button(2,b)
        self.folderbarlist.append(d1)
        self.folderbarlist.append(d2)
        h = d1.rect.height
        d1.rect.topleft = (0, 0)
        d2.rect.topleft = (0, h)
        self.folderbarsprites = pygame.sprite.RenderClear(self.folderbarlist)
    def update(self):
        self.image.blit(self.image2, (0,0))
        self.folderbarsprites.draw(self.image)

class background_bar:
    def __init__(self):
        self.image = pygame.Surface((SIZE[0]- BARSIZE - XDIST, SIZE[1]-BARSIZE*2-BARSIZE_2)).convert()
        self.image.fill(BLACK)
        self.image2 = pygame.Surface((SIZE[0]- BARSIZE - XDIST, SIZE[1]-BARSIZE*2-BARSIZE_2)).convert()
        self.image2.fill(BLACK)
    def write_to(self,a,b):
        self.backgroundlist1 = []
        self.backgroundlist2 = []
        for x in a:
            d = dir_button(3,x)
            self.backgroundlist1.append(d)
        for x in b:
            d = dir_button(4,x)
            self.backgroundlist2.append(d)
        self.dirsprites = pygame.sprite.RenderClear(self.backgroundlist1)
        self.filesprites = pygame.sprite.RenderClear(self.backgroundlist2)
        self.place()
    def place(self,pos=0):
        self.pos = pos
        h = dir_button.image_list[3].get_height()
        self.len_1 = len(self.backgroundlist1)
        self.len_2 = len(self.backgroundlist2)
        len_b = self.len_1 + self.len_2
        self.h_b = h * len_b
        self.is_scrollable = self.h_b > H_B
        if not self.pos:
            count = 0
            for x in self.backgroundlist1:
                x.rect.topleft = (0, count)
                x.ymax = count
                count = count + h
            for x in self.backgroundlist2:
                x.rect.topleft = (0, count)
                x.ymax = count
                count = count + h
        else:
            count = H_B
            self.backgroundlist2.reverse()
            self.backgroundlist1.reverse()
            for x in self.backgroundlist2:
                x.rect.bottomleft = (0, count)
                x.ymax = count
                count = count - h
            for x in self.backgroundlist1:
                x.rect.bottomleft = (0, count)
                x.ymax = count
                count = count - h
            self.backgroundlist2.reverse()
            self.backgroundlist1.reverse()
    def update(self):
        if self.is_scrollable:
            if self.backgroundlist1 and self.backgroundlist2:
                if self.backgroundlist1[0].rect.top > 0:
                    self.place()
                elif self.backgroundlist2[self.len_2-1].rect.bottom < H_B:
                    self.place(1)
            elif self.backgroundlist1 and not self.backgroundlist2:
                if self.backgroundlist1[0].rect.top > 0:
                    self.place()
                elif self.backgroundlist1[self.len_1-1].rect.bottom < H_B:
                    self.place(1)
            elif self.backgroundlist2 and not self.backgroundlist1:
                if self.backgroundlist2[0].rect.top > 0:
                    self.place()
                elif self.backgroundlist2[self.len_2-1].rect.bottom < H_B:
                    self.place(1)
        self.image.blit(self.image2, (0,0))
        self.dirsprites.draw(self.image)
        self.filesprites.draw(self.image)
    def step(self,y):
        if self.is_scrollable:
            _step = int(round((self.h_b / SURFH * 1.0) + 1))
            for x in self.backgroundlist1:
                x.rect = x.rect.move(0, - y*_step)
            for x in self.backgroundlist2:
                x.rect = x.rect.move(0, - y*_step)

class status_bar:
    def __init__(self):
        self.image = pygame.Surface((SIZE[0],BARSIZE)).convert()
        self.image.fill(GREY)

class menu_bar:
    def __init__(self):
        self.image = pygame.Surface((SIZE[0],BARSIZE)).convert()
        self.image.fill(GREY)
        self.menu = menu(self)
    def update(self):
        self.menu.update()

class menu_button(pygame.sprite.Sprite):
    def __init__(self,display_surface,text,tpl,color=BLUE):
        pygame.sprite.Sprite.__init__(self)
        self.display_surface = display_surface
        self.text = text
        self.tpl = tpl
        self.color = color
        self.Font = pygame.font.Font(path.join(HOME_DIRECTORY+'\\data','MgOpenCosmeticaRegular.ttf'),12)
        self.image = self.Font.render(self.text, 1, self.color)
        self.w = self.image.get_width()
        self.h = self.image.get_height()
        self.non_image = pygame.Surface((self.w,self.h)).convert()
        self.non_image.fill(GREY)
        self.rect = self.image.get_rect()
        self.rect.topleft = tpl
        self.display_surface.blit(self.non_image,self.rect)
        self.display_surface.blit(self.image,self.rect)
        self.is_clicked = 0
    def update(self):
        if self.is_clicked:
            self.image = self.Font.render(self.text, 1, WHITE)
            self.display_surface.blit(self.non_image,self.rect)
            self.display_surface.blit(self.image,self.rect)
    def is_focused(self,(x,y)):
        return self.rect.collidepoint(x,y)

class menu:
    def __init__(self,menu_bar):
        self.a = menu_button(menu_bar.image,'Browse',(10,2))
        self.b = menu_button(menu_bar.image,'Settings',(20 + self.a.w, 2))
        self.c = menu_button(menu_bar.image,'About',(30 + self.a.w + self.b.w, 2))
        self.group = [self.a,self.b,self.c]
        self.menusprites = pygame.sprite.Group(self.group)
    def update(self):
        self.menusprites.update()
        if self.a.is_clicked:
            self.b.__init__(self.b.display_surface,self.b.text,self.b.tpl)
            self.c.__init__(self.c.display_surface,self.c.text,self.c.tpl)
            self.a.is_clicked = 0
        elif self.b.is_clicked:
            self.a.__init__(self.a.display_surface,self.a.text,self.a.tpl)
            self.c.__init__(self.c.display_surface,self.c.text,self.c.tpl)
            self.b.is_clicked = 0
        elif self.c.is_clicked:
            self.b.__init__(self.b.display_surface,self.b.text,self.b.tpl)
            self.a.__init__(self.a.display_surface,self.a.text,self.a.tpl)
            self.c.is_clicked = 0

class radio_button(pygame.sprite.Sprite):
    def __init__(self,display_surface,text,tpl,i1='rb0.png'):
        pygame.sprite.Sprite.__init__(self)
        self.display_surface = display_surface
        self.text = text
        self.tpl = tpl
        self.image1 = load_image(i1,-1)
        self.image2 = pygame.Surface((100, 20)).convert()
        self.image2.fill(BLACK)
        display_some_text(self.text, self.image2, 30, 1)
        self.image2.blit(self.image1,(10, 3))
        self.image = self.image2
        self.rect = self.image.get_rect()
        self.rect.topleft = self.tpl
        self.is_dirty = 1
        self.is_clicked = 0
    def update(self):
        if self.is_clicked:
            pygame.draw.rect(self.image1, BLACK, ((5,5),(3,3)), 3)
            self.image2.blit(self.image1,(10, 3))
        elif not self.is_clicked:
            pygame.draw.rect(self.image1, WHITE, ((5,5),(3,3)), 3)
            self.image2.blit(self.image1,(10, 3))
        if self.is_dirty:
            self.display_surface.blit(self.image,self.rect)
            self.is_dirty = 0
    def is_focused(self,(x,y)):
        return self.rect.collidepoint(x,y)

class radio_button_holder:
    def __init__(self,text,namelist,tpl,screen):
        self.text = text
        self.namelist = namelist
        self.label = pygame.Surface((100, 20)).convert()
        self.label.fill(BLACK)
        screen.lock()
        pygame.draw.rect(screen, BLUE, (tpl,(100, 20*(len(namelist)+1))), 3)
        screen.unlock()
        display_some_text(self.text, self.label, 10, 1)
        self.rect = self.label.get_rect()
        self.rect.topleft = tpl
        screen.blit(self.label,self.rect)
        self.group = []
        for x in namelist:
            tpl[1] = tpl[1] + 20
            a = radio_button(screen,x,tpl)
            if a.text in ['44100','16','Yes','4096']:
                a.is_clicked = 1
            self.group.append(a)
        self.radiosprites = pygame.sprite.Group(self.group)
    def update(self):
        for x in self.group:
            if x.is_dirty and x.is_clicked:
                a,b = slice_the_list(x,self.group)
                if a:
                    for y in a:
                        if y.is_clicked:
                            y.is_clicked = 0
                            y.is_dirty = 1
                if b:
                    for y in b:
                        if y.is_clicked:
                            y.is_clicked = 0
                            y.is_dirty = 1
        self.radiosprites.update()

class about_screen:
    def __init__(self,screen):
        self.screen = screen
        text_file = path.join(HOME_DIRECTORY+'\\data','info2.txt')
        in_file = open(text_file,"r")
        self.text = in_file.readlines()
        in_file.close()
        self.text2 = []
        for t in self.text:
            lt = len(t)-1
            t2 = t[:lt]
            self.text2.append(t2)
        self.count = 0
        self.update()
    def update(self):
        self.screen.fill(BLACK,((0,BARSIZE),(SIZE[0],SIZE[1]-BARSIZE)))
        linelist = []
        for s in self.text2[self.count:]:
            self.count = self.count + 1
            if s == '^' or s == 'end':
                break
            else:
                linelist.append(s)
        if not s == 'end':
            y = SIZE[1] - 20 - (len(linelist)*14)
            maxlen = 0
            for line in linelist:
                ll = len(line)
                if ll > maxlen:
                    maxlen = ll
                display_some_text(line,self.screen,20,0,y,1)
                y = y + 14
            display_some_text('... click',self.screen,maxlen*5,0,y,1)
        else:
            self.__init__(self.screen)

class browser:
    def __init__(self,a):
        b = create_dirs(a)
        self.ba = background_bar()
        self.ba.write_to(b[2],b[3])
        self.fo = folder_bar()
        self.fo.write_to(b[0],b[1])
        self.sc = scroll_bar(self.ba.h_b,self.ba.is_scrollable)
    def update(self):
        self.ba.update()
        self.fo.update()
        self.sc.update()

class non_browser:
    def __init__(self):
        self.me = menu_bar()
        self.st = status_bar()
    def update(self):
        self.me.update()

class game:
    def __init__(self,screen,ground):
        a, a2 = browse(screen,ground)
        run = 1
        while run:
            if a == 0:
                run = 0
            elif a == 1:
                b = settings(screen,ground)
                if b == 0:
                    run = 0
                elif b == 1:
                    a = 2
                elif b == 2:
                    a, a2 = browse(screen,ground,a2)
            elif a == 2:
                c = about(screen,ground)
                if c == 0:
                    run = 0
                elif c == 1:
                    a = 1
                elif c == 2:
                    a, a2 = browse(screen,ground,a2)
        quit_drives()
        pygame.quit()

#-------------------Game functions-------------------
def settings(screen,ground):
    global SAMPLING_RATE, SAMPLE_SIZE, STEREO, BUFFER_SIZE
    ret = 0
    run = 1

    x1 = 30
    y1 = 10

    a = radio_button_holder('Sampling rate', ['8000', '11025', '22050', '32000', '44100'], [x1+10,y1+30], screen)
    for y in a.group:
        if y.text == str(SAMPLING_RATE): y.is_clicked = 1
    b = radio_button_holder('Sample size', ['8', '16'], [x1+120,y1+30], screen)
    for y in b.group:
        if y.text == str(SAMPLE_SIZE): y.is_clicked = 1
    c = radio_button_holder('Stereo', ['No', 'Yes'], [x1+120,y1+100], screen)
    if STEREO == 1:
        _STEREO = 'No'
    else:
        _STEREO = 'Yes'
    for y in c.group:
        if y.text == _STEREO: y.is_clicked = 1
    d = radio_button_holder('Buffer size', ['512', '1024', '2048', '4096'], [x1+230,y1+30], screen)
    for y in d.group:
        if y.text == str(BUFFER_SIZE): y.is_clicked = 1

    display_some_text('for .ogg, .wav & .xm files',screen,240,0,175,1)

    n = non_browser()
    n.me.menu.b.is_clicked = 1

    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = 0
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for x in n.me.menu.group:
                        if x.is_focused((event.pos[0],event.pos[1])):
                            x.is_clicked = 1
                            ret2 = n.me.menu.group.index(x)
                            if ret2 == 0:
                                ret = 2
                                run = 0
                            elif ret2 == 2:
                                ret = 1
                                run = 0
                    for x in [a.group, b.group, c.group, d.group]:
                        for y in x:
                            if y.is_focused((event.pos[0],event.pos[1])):
                                y.is_clicked = 1
                                y.is_dirty = 1

        pygame.event.pump()
        a.update()
        b.update()
        c.update()
        d.update()
        n.update()
        a.radiosprites.draw(screen)
        b.radiosprites.draw(screen)
        c.radiosprites.draw(screen)
        d.radiosprites.draw(screen)
        screen.blit(n.me.image, (0, 0))
        pygame.display.update()

    for v in a.radiosprites:
        v.kill()
    for v in b.radiosprites:
        v.kill()
    for v in c.radiosprites:
        v.kill()
    for v in d.radiosprites:
        v.kill()
    for v in n.me.menu.menusprites:
        v.kill()

    screen.fill(BLACK,((0,BARSIZE),(SIZE[0],SIZE[1]-BARSIZE)))
    pygame.display.update()

    for y in a.group:
        if y.is_clicked:
            SAMPLING_RATE_2 = int(y.text)
    for y in b.group:
        if y.is_clicked:
            SAMPLE_SIZE_2 = int(y.text)
    for y in c.group:
        if y.is_clicked:
            if y.text == 'No':
                STEREO_2 = 1
            else:
                STEREO_2 = 2
    for y in d.group:
        if y.is_clicked:
            BUFFER_SIZE_2 = int(y.text)

    if [SAMPLING_RATE, SAMPLE_SIZE, STEREO, BUFFER_SIZE] != [SAMPLING_RATE_2, SAMPLE_SIZE_2, STEREO_2, BUFFER_SIZE_2]:
        [SAMPLING_RATE, SAMPLE_SIZE, STEREO, BUFFER_SIZE] = [SAMPLING_RATE_2, SAMPLE_SIZE_2, STEREO_2, BUFFER_SIZE_2]
        pygame.mixer.quit()
        quit_drives()
        pygame.mixer.init(SAMPLING_RATE, SAMPLE_SIZE, STEREO, BUFFER_SIZE)

    return ret

def about(screen,ground):
    ret = 0
    run = 1

    n = non_browser()
    n.me.menu.b.is_clicked = 1
    a = about_screen(screen)

    song = path.join(HOME_DIRECTORY+'\\data','GODREST.mid')
    play(song,n.st.image)

    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = 0
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for x in n.me.menu.group:
                        if x.is_focused((event.pos[0],event.pos[1])):
                            x.is_clicked = 1
                            ret2 = n.me.menu.group.index(x)
                            if ret2 == 0:
                                ret = 2
                                run = 0
                            elif ret2 == 1:
                                ret = 1
                                run = 0
                    if event.pos[1] in range(BARSIZE,SIZE[1]):
                        a.update()

        pygame.event.pump()
        n.update()
        pygame.display.update()

    for v in n.me.menu.menusprites:
        v.kill()
    screen.fill(BLACK,((0,BARSIZE),(SIZE[0],SIZE[1]-BARSIZE)))
    pygame.display.update()
    pygame.mixer.music.stop()
    return ret

def browse(screen,ground,top=None):

    if top == 1:
        cwd = 'My Computer'
        b = browser(RANDOM_NUMBER)
    else:
        cwd = getcwd()
        b = browser(cwd)

    n = non_browser()
    n.me.menu.a.is_clicked = 1
    _print(n.st.image, cwd)

    ret = 0
    run = 1
    dragging = False
    z = 0
    click_flag = 0

    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = 0
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    for x in n.me.menu.group:
                        if x.is_focused((event.pos[0],event.pos[1])):
                            x.is_clicked = 1
                            ret = n.me.menu.group.index(x)
                            if ret in [1,2]: run = 0
                    if b.fo.folderbarlist[0].is_focused((event.pos[0],event.pos[1] - BARSIZE)):
                        if b.fo.a == 1: break
                        aaa = getcwd()
                        bbb = go_up(aaa)
                        b.__init__(bbb)
                        if bbb == RANDOM_NUMBER: _print(n.st.image,'My Computer')
                        else: _print(n.st.image, bbb)
                    if event.pos[1] in range(BYR1,BYR2):
                        for x in b.ba.backgroundlist1:
                            if x.is_focused((event.pos[0],event.pos[1] - BB)):
                                click_flag = 1
                                try:
                                    for v in b.fo.folderbarsprites:
                                        v.kill()
                                    for v in b.ba.dirsprites:
                                        v.kill()
                                    for v in b.ba.filesprites:
                                        v.kill()
                                    aaa = getcwd()
                                    if path.ismount(aaa) and b.fo.a:
                                        b.__init__(x.text)
                                        _print(n.st.image, x.text)
                                    else:
                                        b.__init__(aaa + '\\' + x.text)
                                        _print(n.st.image, aaa + '\\' + x.text)
                                except OSError:
                                    aaa = getcwd()
                                    if not b.fo.a: b.__init__(aaa)
                                    else: b.__init__(RANDOM_NUMBER)
                                    _print(n.st.image,"Permission denied: '" + x.text + "'")
                                    continue
                        for x in b.ba.backgroundlist2:
                            if x.is_focused((event.pos[0],event.pos[1] - BB)) and not click_flag:
                                aaa = getcwd()
                                song = aaa + '\\' + x.text
                                play(song,n.st.image)
                    if b.sc.a.is_focused(event.pos):
                        b.sc.a.is_clicked = 1
                        z = z - 3
                    if b.sc.b.is_focused(event.pos):
                        b.sc.b.is_clicked = 1
                        z = z + 3
                    if b.sc.c.is_focused(event.pos) and not b.sc.d.is_focused(event.pos):
                        b.sc.c.is_clicked = 1
                        if event.pos[1] <= b.sc.d.rect.top: z = z - 7
                        elif event.pos[1] >= b.sc.d.rect.bottom: z = z + 7
                    if b.sc.d.is_focused(event.pos): b.sc.d.is_clicked = 1
                elif event.button == 4: z = z - 7
                elif event.button == 5: z = z + 7
                b.sc.d.move(0,z)
                b.ba.step(z)

            elif event.type == MOUSEBUTTONUP:
                dragging = False
                z = 0
                click_flag = 0
                for x in b.sc.group:
                    x.is_clicked = 0

            elif event.type == MOUSEMOTION:
                if dragging:
                    y = event.rel[1]
                    if b.sc.d.is_clicked:
                        b.sc.d.move(0,y)
                        b.ba.step(y)

        pygame.event.pump()
        b.update()
        b.sc.scrollbarsprites.draw(screen)
        n.update()
        screen.blit(b.ba.image, (0, BARSIZE + BARSIZE_2))
        screen.blit(b.fo.image, (0, BARSIZE))
        screen.blit(n.me.image, (0, 0))
        screen.blit(n.st.image, (0, BARSIZE + BARSIZE_2 + H_B))
        pygame.display.update()

    for v in n.me.menu.menusprites:
        v.kill()
    for v in b.fo.folderbarsprites:
        v.kill()
    for v in b.ba.dirsprites:
        v.kill()
    for v in b.ba.filesprites:
        v.kill()
    for v in b.sc.scrollbarsprites:
        v.kill()

    screen.fill(BLACK,((0,BARSIZE),(SIZE[0],SIZE[1]-BARSIZE)))
    pygame.display.update()

    return ret, b.fo.a

def main():
    pygame.mixer.pre_init(SAMPLING_RATE, SAMPLE_SIZE, STEREO, BUFFER_SIZE)
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("PyMP v" + VERSION)
    pygame.display.update()

    ground = pygame.Surface(screen.get_size())
    ground = ground.convert()
    ground.fill((0,0,0))

    a = game(screen,ground)

if __name__ == '__main__': main()
