from tkinter import Toplevel
import pygame
from pygame import K_w, key
import random
from pygame import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
RED, GREEN, BLUE, BLACK, WHITE = ((255, 0, 0),(0,255,0),(0,0,255),(0,0,0),(255,255,255))

class character(pygame.sprite.Sprite):
    def __init__(self, x, y, HP, OnGround, CharacterSirka, CharacterVyska):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2()
        self.HP = HP
        self.OnGround = OnGround
        self.image = pygame.Surface((CharacterSirka, CharacterVyska))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))
        self.Zet = 1 #pro potreby zmeny Postavy mezi plazenim a stojenim
        self.cooldown = 0   #Cooldown mezi zmenenim stavu (stani/plazeni)
        self.GroundSpeed = 250  #rychlost pohybu normalne
        self.ClimbSpeed = 100
        self.IsCrawling = False
        self.IsClimbing = False

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

        # Horizontalni movement
        self.vel.x = 0
        if pressed[pygame.K_LEFT]:# or pressed[pygame.K_a]:
            self.vel.x -= self.GroundSpeed
        if pressed[pygame.K_RIGHT]:# or pressed[pygame.K_d]:
            self.vel.x += self.GroundSpeed

        # Skakani
        if pressed[pygame.K_UP] and self.OnGround and not self.IsClimbing:
            self.vel.y = -1135 if self.Zet == 1 else -300
            self.OnGround = False  # Immediately set OnGround to False when jumping

        if pressed[pygame.K_f] and self.MuzesLezt:
            self.IsClimbing = True
        else:
            self.IsClimbing = False

        if self.IsClimbing:
            if pressed[pygame.K_UP]:
                self.vel.y = -self.ClimbSpeed
            elif pressed[pygame.K_DOWN]:
                self.vel.y = self.ClimbSpeed
            else:
                self.vel.y = 0  # Zustanes na miste pokud se nehejbes
        elif not self.OnGround:
            # Gravity (only if not climbing and not on ground)
            self.vel.y += 5000 * time_passed
        else:
            # Na zemi
            self.vel.y = 0

        # Updejt pozic a check kolizi pro X a Y
        self.pos.x += self.vel.x * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_x(blocks)

        self.pos.y += self.vel.y * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_y(blocks)

        # abys nahodou neodesel z obrazovky
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        if self.rect.right > 1280:
            self.rect.right = 1280
            self.pos.x = self.rect.centerx

        return pressed

    def check_collisions_x(self, blocks):
        self.MuzesLezt = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                self.MuzesLezt = True
                if self.vel.x > 0:  # Pohyb doprava
                    self.rect.right = block.rect.left
                elif self.vel.x < 0:  # Pohyb doleva
                    self.rect.left = block.rect.right
                self.pos.x = self.rect.centerx
                break  # Brejk kdyz je nalezena kolize

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
                self.pos.y = self.rect.bottom
                break

        if self.IsClimbing and not self.MuzesLezt:
            self.IsClimbing = False

    def camera_movement(self):
        TopLine = pygame.draw.line(screen, GREEN,(0, 200),(1280, 200), 5)
        BottomLine = pygame.draw.line(screen, GREEN,(0, 600),(1280, 600), 5)
        LeftLine = pygame.draw.line(screen, GREEN,(400, 0),(400, 720), 5)
        RightLine = pygame.draw.line(screen, GREEN,(880, 0),(880, 720), 5)


Hrac = character(640, 360, 100, OnGround = True, CharacterSirka = 50, CharacterVyska = 150)

HracSprite = pygame.sprite.GroupSingle()
HracSprite.add(Hrac)

class environmentblock(pygame.sprite.Sprite):
    def __init__(self, x, y, sirka, vyska):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.move = pygame.math.Vector2()
        self.sirka = sirka
        self.vyska = vyska
        self.image = pygame.Surface((self.sirka, self.vyska))
        self.image.fill((255, 255, 255)) 
        self.rect = self.image.get_rect(topleft=(round(self.pos.x), round(self.pos.y)))


AllCaveSprites = pygame.sprite.Group()
Bloky = (environmentblock(0, 540, 1280, 50), #podlaha
         environmentblock(0,0, 10, 720)) #lezecka stena
for i in range(18):
    x = (environmentblock((random.randint(0,1230)), (random.randint(400,550)), 50, 50))
    AllCaveSprites.add(x)
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
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))
        self.Speed = 100  #Rychlost pohybu
        self.CanCPlayer = False

    def update(self, time_passed, blocks):
        self.move.y += 5000 * time_passed  #Gravitace

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
            player_bottom = (Hrac.rect.center[0], Hrac.rect.bottom - 10)
            player_top = (Hrac.rect.center[0], Hrac.rect.top + 10)
            enemy_top = (self.rect.center[0], self.rect.top + 20)
            
            self.CanCPlayer_Top = True
            self.CanCPlayer_Center = True
            
            if self.move.x > 0: #pohyb doprava
                self.Doprava = True
                self.Doleva = False

            elif self.move.x < 0:
                self.Doleva = True
                self.Doprava = False

            #checkujes dvakrat, protoze jednou je to pro vrchol hrace a jednou pro spodek hrace
            for block in AllCaveSprites:
                if block.rect.clipline(player_bottom, enemy_top):
                    self.CanCPlayer_Center = False
                    break  #Jakmile neco blokuje vyhled enemy brejkujes loop
            for block in AllCaveSprites:
                if block.rect.clipline(player_top, enemy_top):
                    self.CanCPlayer_Top = False
                    break  #Jakmile neco blokuje vyhled enemy brejkujes loop

    
            #vykreslovani
            if self.CanCPlayer_Center:
                pygame.draw.line(screen, RED, player_bottom, enemy_top, 5)
            else:
                pygame.draw.line(screen, GREEN, player_bottom, enemy_top, 5)
            if self.CanCPlayer_Top:
                pygame.draw.line(screen, RED, player_top, enemy_top, 5)
            else:
                pygame.draw.line(screen, GREEN, player_top, enemy_top, 5)

            if self.CanCPlayer_Center or self.CanCPlayer_Top:
                pass
                # self.hunt()


    def killCheck(self):
        kolizeCheck = pygame.sprite.spritecollide(Hrac, EnemySprite, False)
        if kolizeCheck:
            print('ted ma hrac umrit')

class GameClock:
    def __init__(self, target_fps=60):
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.last_time = time.get_ticks()
        self.fixed_delta = 1.0 / target_fps
        
    def tick(self):
        """Returns a fixed delta time regardless of actual frame time"""
        current_time = time.get_ticks()
        delta = (current_time - self.last_time) / 1000.0
        self.last_time = current_time
        
        # Cap delta time to prevent huge jumps
        if delta > 0.25:  # Cap at 1/4 second
            delta = self.fixed_delta
            
        self.clock.tick(self.target_fps)
        return self.fixed_delta  # Return fixed timestep instead of actual delta


Nepritel = Enemy(1000, 400, True)
EnemySprite = pygame.sprite.Group()
EnemySprite.add(Nepritel)

game_clock = GameClock(60)



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    delta_time = game_clock.tick()

    Hrac.update(delta_time, AllCaveSprites)
    Hrac.camera_movement()
    Nepritel.update(delta_time, AllCaveSprites)
    Nepritel.patrol(Hrac, screen, AllCaveSprites)
    Nepritel.killCheck()

    HracSprite.draw(screen)
    EnemySprite.draw(screen)
    AllCaveSprites.draw(screen)
    pygame.display.flip()

pygame.quit()