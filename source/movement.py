import pygame
from pygame import key
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

class character(pygame.sprite.Sprite):
    def __init__(self, x, y, HP, OnGround, CharacterSirka, CharacterVyska):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2()
        self.HP = HP
        self.OnGround = OnGround
        self.image = pygame.Surface((CharacterSirka, CharacterVyska))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))
        self.Zet = 1 #pro potreby zmeny Postavy mezi plazenim a stojenim
        self.cooldown = 0   #Cooldown mezi zmenenim stavu (stani/plazeni)
        self.GroundSpeed = 250  #rychlost pohybu normalne

    def update(self, time_passed, blocks):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RCTRL]:
            if self.cooldown <= 0:
                if self.Zet == 1: #TOTO JE PLAZENI
                    self.CharacterSirka, self.CharacterVyska= 150, 50
                    self.GroundSpeed = 50
                    self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
                    self.image.fill((255, 0, 0))
                    self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))
                    self.Zet *= -1
                elif self.Zet == -1: #TOHLE JE KDYZ HRAC STOJI
                    self.CharacterSirka, self.CharacterVyska= 50, 150
                    self.GroundSpeed = 250
                    self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
                    self.image.fill((255, 0, 0))
                    self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))
                    self.Zet *= -1
                self.cooldown = 0.2  #cooldown protoze to je vic "hardcore" :)
                #also toto cele se da prepsat na 3 radky takze look into that

        if self.cooldown > 0:
            self.cooldown -= time_passed

        # Horizontal movement
        self.vel.x = 0
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            self.vel.x -= self.GroundSpeed
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.vel.x += self.GroundSpeed

        # Jumping
        if (pressed[pygame.K_UP] or pressed[pygame.K_w]) and self.OnGround:
            self.vel.y -= 1135 if self.Zet == 1 else 300

        # Apply gravity
        self.vel.y += 5000 * time_passed

        # Update position and check collisions
        self.pos.x += self.vel.x * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_x(blocks)

        self.pos.y += self.vel.y * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_y(blocks)

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        if self.rect.right > 1280:
            self.rect.right = 1280
            self.pos.x = self.rect.centerx

        return pressed

    def check_collisions_x(self, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel.x > 0:  # Moving right
                    self.rect.right = block.rect.left
                elif self.vel.x < 0:  # Moving left
                    self.rect.left = block.rect.right
                self.pos.x = self.rect.midbottom[0]

    def check_collisions_y(self, blocks):
        self.OnGround = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel.y > 0:  # Falling
                    self.rect.bottom = block.rect.top
                    self.vel.y = 0
                    self.OnGround = True
                elif self.vel.y < 0:  # Jumping
                    self.rect.top = block.rect.bottom
                    self.vel.y = 0
                self.pos.y = self.rect.midbottom[1]

Hrac = character(100, 700, 100, OnGround = False, CharacterSirka = 50, CharacterVyska = 150)

HracSprite = pygame.sprite.GroupSingle()
HracSprite.add(Hrac)

class environmentblock(pygame.sprite.Sprite):
    def __init__(self, x, y, sirka, vyska):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.move = pygame.math.Vector2()
        self.sirka = sirka
        self.vyska = vyska
        self.Top_col = False
        self.Bot_col = False
        self.Lef_col = False
        self.Rig_col = False
        self.image = pygame.Surface((self.sirka, self.vyska))
        self.image.fill((255, 255, 255)) 
        self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))

AllCaveSprites = pygame.sprite.Group()
Bloky = (environmentblock(300, 680, 100, 20),environmentblock(850, 480, 100, 20),environmentblock(600, 610, 100, 20),environmentblock(850, 180, 100, 20),
         environmentblock(640, 710, 1280, 20),
         environmentblock(720, 690, 100, 200))
AllCaveSprites.add(Bloky)

OnTopBlock = True #jak vim ze je postava na hore na bloku a nemam aplikovat teleport do strany
jumping = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, OnGround):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.move = pygame.math.Vector2(100, 0)  # Initial velocity
        self.OnGround = OnGround
        self.image = pygame.Surface((80, 200))
        self.image.fill((200, 0, 200)) 
        self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))
        self.Speed = 100  #Rychlost pohybu
        self.CanCPlayer = False

    def update(self, time_passed, blocks):
        self.move.y += 5000 * time_passed  # Gravity

        # Update position and check collisions
        self.pos.x += self.move.x * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_x(blocks)

        self.pos.y += self.move.y * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_y(blocks)

        # Screen boundaries
        if self.rect.left < 0 or self.rect.right > 1280:
            self.move.x *= -1
        self.rect.clamp_ip(screen.get_rect())
        self.pos.x, self.pos.y = self.rect.midbottom

    def check_collisions_x(self, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.move.x > 0:  # Moving right
                    self.rect.right = block.rect.left
                elif self.move.x < 0:  # Moving left
                    self.rect.left = block.rect.right
                self.move.y -= 1000
                self.move.x *= -1  # Reverse direction
                self.pos.x = self.rect.midbottom[0]


    def check_collisions_y(self, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.move.y > 0:  # Falling
                    self.rect.bottom = block.rect.top
                    self.move.y = 0
                    self.OnGround = True
                elif self.move.y < 0:  # Jumping
                    self.rect.top = block.rect.bottom
                    self.move.y = 0
                self.pos.y = self.rect.midbottom[1]

    def patrol(self, Hrac, screen, AllCaveSprites):
            player_center = Hrac.rect.center
            enemy_center = self.rect.center
            pygame.draw.line(screen,(255, 0, 0), player_center, enemy_center, 5)
            for block in AllCaveSprites:
                if block.rect.clipline((player_center, enemy_center)):
                    pygame.draw.line(screen, (0,0,255), player_center, enemy_center, 5)
                    self.CanCPlayer = False
                else:
                    self.CanCPlayer = True
            if self.CanCPlayer:
                print("ted vidi Hrace")
                # self.hunt()

        

    def killCheck(self):
        kolizeCheck = pygame.sprite.spritecollide(Hrac, EnemySprite, False)
        if kolizeCheck:
            print('ted ma hrac umrit')

Nepritel = Enemy(1000, 500, True)
EnemySprite = pygame.sprite.Group()
EnemySprite.add(Nepritel)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    time_passed = clock.tick(60) / 1000.0

    Hrac.update(time_passed, AllCaveSprites)
    Nepritel.update(time_passed, AllCaveSprites)
    Nepritel.patrol(Hrac, screen, AllCaveSprites)
    Nepritel.killCheck()

    HracSprite.draw(screen)
    EnemySprite.draw(screen)
    AllCaveSprites.draw(screen)
    pygame.display.flip()

pygame.quit()