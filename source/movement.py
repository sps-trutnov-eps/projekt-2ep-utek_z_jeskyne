import pygame
from pygame import key

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
OnGround = True


class character:
    def __init__(self, x, y, HP, OnGround):
        self.x = x
        self.y = y
        self.HP = HP
        self.OnGround = OnGround
    def draw(self, screen, x, y):
        pygame.draw.rect(screen, (255, 0, 0), (x, y, 50, 100))
    def moveIT(self, x, y, OnGround):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if not self.OnGround:
                self.x -= 5
            else:
                self.x -= 10
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.OnGround:
                self.y -= 120
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not self.OnGround:
                self.x += 5
            else:
                self.x += 10

        if self.y >= 720 - 100:
            self.y = 720 - 100
        if self.y < 720 - 100:
            self.y += 2.3
            self.OnGround = False
        else:
            self.OnGround = True


Hrac = []
Hrac.append(character(100, 720 - 100, 100, OnGround))

class environmentblock:
    def __init__(self, x, y, xx, yy):
        self.x = x
        self.y = y
        self.xx = xx
        self.yy = yy
    def draw(self, screen, x, y, xx, yy):
        pygame.draw.rect(screen, (255, 255, 255), (x, y, xx, yy))
Cave = []
Cave.append(environmentblock(300, 650, 200, 40))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    screen.fill((0,0,0))


    for character in Hrac:
        character.draw(screen, character.x, character.y)
        character.moveIT(character.x, character.y, OnGround)

    for block in Cave:
        block.draw(screen, block.x, block.y, block.xx, block.yy)




    pygame.display.flip()

    clock.tick(60)

pygame.quit()