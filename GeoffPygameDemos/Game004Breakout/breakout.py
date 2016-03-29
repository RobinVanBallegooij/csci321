#!/usr/bin/env python
#
# Geoff's Breakout

VERSION = "0.1"

import pygame, random, os, math, sys
from pygame.locals import *

BALL_SPEED = 8
BAT_SPEED = 6
BORDER = 32
BRICK_WIDTH, BRICK_HEIGHT = (32,16)
WIDTH,HEIGHT = (640,480)

def load_image(name, folder = 'data', colorkey=-1):
    fullname = os.path.join(folder, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name, folder = 'sounds'):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(folder, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

class Sound():
    def __init__(self):
        self.deepsound = load_sound('beep1.wav')
        self.highsound = load_sound('beep5.wav')

    def deep(self):
        self.deepsound.play()
    def high(self):
        self.highsound.play()

class Brick(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('stone02.gif',
                                           folder='sprites')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = pos

class Ball(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('ball1.gif', folder='sprites')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = pos
        self.prevpos = pos
        self.hit = 1
        self.reset()

    def reset(self):
        self.hspeed = self.vspeed = 0
        self.state = 'still'

    def setAngle(self, angle):
        self.hspeed = BALL_SPEED * math.cos(angle)
        self.vspeed = -BALL_SPEED * math.sin(angle)

    def update(self):
        ## Follow the bat:
        if self.state == 'still':
            self.rect.midbottom = bat.rect.midtop
            return
            
        ## Normal movement:
        if abs(self.hspeed) < 0.5:
            self.hspeed = random.choice((-0.5,0.5))
        self.prevpos = self.rect.topleft
        self.rect.left += self.hspeed
        self.rect.top += self.vspeed

        ## Border collisions:
        if self.rect.left < BORDER:
            sound.high()
            self.rect.topleft = self.prevpos
            self.hspeed = -self.hspeed
        if self.rect.right > WIDTH-BORDER:
            sound.high()
            self.rect.topleft = self.prevpos
            self.hspeed = -self.hspeed
        if self.rect.top < BORDER:
            sound.high()
            self.rect.topleft = self.prevpos
            self.vspeed = -self.vspeed
        if self.rect.top > HEIGHT:
            score.score -= 50
            self.reset()
            return

        ## Brick collisions
        collidebricks = pygame.sprite.spritecollide(self, bricks, 1)
        for brick in collidebricks:
            score.score += 10
        if collidebricks:
            sound.deep()
            self.rect.topleft = self.prevpos
            brick = collidebricks[0]
            x = brick.rect.centerx - self.rect.centerx
            y = self.rect.centery - brick.rect.centery
            if abs(x) > 2*abs(y):
                self.hspeed = -self.hspeed
            else:
                self.vspeed = -self.vspeed

        ## Bat collisions
        collidebat = pygame.sprite.spritecollide(self, bats, 0)
        if collidebat:
            if not self.hit:
                sound.high()
            self.rect.topleft = self.prevpos
            angle = 2*(bat.rect.centerx - self.rect.centerx)
            angle = (angle/180.0)*math.pi+math.pi/2.0
            self.hspeed = BALL_SPEED * math.cos(angle)
            self.vspeed = -BALL_SPEED * math.sin(angle)
        if self.hit:
            self.hit = not self.hit
                
class Bat(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('bat1.gif', folder='sprites')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = pos
        self.speed = 0

    def update(self):
        if self.rect.left < BORDER:
            self.speed = 0
            self.rect.left = BORDER
        if self.rect.right > WIDTH-BORDER:
            self.speed = 0
            self.rect.right = WIDTH-BORDER
        self.rect.centerx += self.speed
        self.rect.right = min(WIDTH-BORDER, self.rect.right)
        self.rect.left  = max(BORDER, self.rect.left)

    def setSpeed(self, speed):
        self.speed = speed

class Score():
    def __init__(self):
        self.score = 0
        self.font = pygame.font.Font(None, 16)

    def draw(self, screen):
        text = 'Score: ' + str(self.score)
        score = self.font.render(text, 1, (240,240,240))
        screen.blit(score, (8,8))

def gameOver():
    global screen,score,bricks,ball,objects
    screen.blit(background, (0,0))
    ball.state = 'still'
    ball.update()
    balls.draw(screen)
    bats.draw(screen)
    font = pygame.font.Font(None, 64)
    text = "Game Over"
    over = font.render(text, 1, (240,240,240))
    screen.blit(over, (WIDTH*0.25,HEIGHT*0.25))
    font = pygame.font.Font(None, 32)
    over = font.render("Score: " + str(score.score), 1, (240,240,240))
    screen.blit(over, (WIDTH*0.25,HEIGHT*0.5))
    pygame.display.flip()
    wait = 1
    while (wait):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_F1:
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH,HEIGHT))
                        fullscreen = not(fullscreen)
                elif event.key == K_SPACE:
                    wait = 0
    loadBackground()
#    bricks.add(Brick((100,200)))
    for x in range(BRICK_WIDTH*2, WIDTH-BRICK_WIDTH*2, BRICK_WIDTH):
        for y in range(BRICK_HEIGHT*4, BRICK_HEIGHT*8, BRICK_HEIGHT):
            bricks.add(Brick((x,y)))
    loadBackground()
    screen.blit(background, (0,0))
    objects.add(bricks)
    score.score = 0
    objects.update()
    objects.draw(screen)
    score.draw(screen)
    pygame.display.flip()
        
def loadBackground():
    global background
    bgdir = os.listdir('backgrounds')
    bgimages = [f for f in bgdir if f[-4:] == '.png']
    background, brect = load_image(random.choice(bgimages),
                                   folder='backgrounds',
                                   colorkey=None)
    ## Draw border around background
    for offset in range(0,BORDER):
        a = (offset, HEIGHT)
        b = (offset, offset)
        c = (WIDTH-offset, offset)
        d = (WIDTH-offset, HEIGHT)
        # medium grays:
        col = 64 + offset*3 
        pygame.draw.lines(background, (col,col,col), 0, (a,b,c,d))

def main():
    global background,balls,bats,bricks,bat,ball,score,screen,objects,sound

    pygame.mixer.pre_init(8000)
    pygame.init()
    sound = Sound()
    fullscreen = False
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Geoff's Breakout")
    pygame.mouse.set_visible(False)
        
    loadBackground()
    screen.blit(background, (0,0))
    pygame.display.flip()

    score = Score()
    ball = Ball((0,0))
    balls = pygame.sprite.RenderPlain(ball)
    bat = Bat((WIDTH/2, HEIGHT-BORDER))
    bats = pygame.sprite.RenderPlain(bat)
#    bricks = pygame.sprite.RenderPlain(Brick((100,200)))
    bricks = pygame.sprite.RenderPlain()
    for x in range(BRICK_WIDTH*2, WIDTH-BRICK_WIDTH*2, BRICK_WIDTH):
        for y in range(BRICK_HEIGHT*4, BRICK_HEIGHT*8, BRICK_HEIGHT):
            bricks.add(Brick((x,y)))
    objects = pygame.sprite.RenderPlain((bats, bricks, balls))
    
    clock = pygame.time.Clock()
    while 1:
        if len(bricks) == 0:
            gameOver()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_F1:
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH,HEIGHT))
                    fullscreen = not(fullscreen)
                elif event.key == K_LEFT:
                    bat.speed = -10
                elif event.key == K_RIGHT:
                    bat.speed = 10
                elif event.key == K_SPACE and ball.state == 'still':
                    ball.state = 'moving'
                    ball.vspeed = 12
            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    bat.speed = 0

        screen.blit(background, (0,0))
        objects.update()
        objects.draw(screen)
        score.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
        ## if pygame.quit is not called, things get very wonky in idle,
        ## so we make sure it gets called whether or not an exception is
        ## raised.  This also allows us to symply call sys.exit (which
        ## raises SystemExit) to quit the game in medias res, and still
        ## make sure pygame.quit is called.
    

    
