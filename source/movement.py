import pygame
from pygame import K_w, key, time
import random
#from tkinter import Toplevel

screen = pygame.display.set_mode((1280, 720))
COLORS = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255)
}

def initGame():
    game_state = GameState()
    
    # Initialize basic Pygame
    game_state.screen, game_state.clock = initPygame()
    
    # Create player
    game_state.player = character(
        0, 100, 100,
        OnGround=True,
        CharacterSirka=50,
        CharacterVyska=150
    )
    
    #Sprite Hrace
    game_state.HracSprite = pygame.sprite.GroupSingle()
    game_state.HracSprite.add(game_state.player) 
    
    #Inicializace Kamery
    game_state.camera = Camera(game_state.player, 1280, 720)
    
    #Postav mapu, upec chleba
    game_state.AllCaveSprites = CreateMap()
    
    #Enemy init, pozdejc jich asi bude vic
    enemy = Enemy(1000, 400, True)
    game_state.enemy_sprite = pygame.sprite.Group()
    game_state.enemy_sprite.add(enemy)
    
    #inicializuj gameclock, kterej se jen stara o to abys mohl hejbat s oknem a nepokazilo to timing
    game_state.game_clock = GameClock(60)
    
    return game_state

class character(pygame.sprite.Sprite):
    def __init__(self, x, y, HP, OnGround, CharacterSirka, CharacterVyska):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2()
        self.HP = HP
        self.OnGround = OnGround
        self.CharacterSirka = CharacterSirka
        self.CharacterVyska = CharacterVyska
        self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))
        self.cooldown = 0   #Cooldown mezi zmenenim stavu (stani/plazeni)
        self.GroundSpeed = 250  #rychlost pohybu normalne
        self.ClimbSpeed = 100
        self.CanStandUp = True
        self.IsCrawling = False
        self.IsCrawling = False
        self.IsClimbing = False

    def update(self, time_passed, blocks):
        self.CanStandUp = True
        pressed = pygame.key.get_pressed()

        SpaceCheckHeight = self.CharacterVyska if not self.IsCrawling else 150 
        SpaceCheckerRect = pygame.Rect(self.rect.x, self.rect.y - (SpaceCheckHeight - self.CharacterVyska), self.CharacterSirka,SpaceCheckHeight - self.CharacterVyska)
        
        for block in blocks:
            if SpaceCheckerRect.colliderect(block.rect):
                self.CanStandUp = False
                print("ted se nemuzes postavit")
                break
            else:
                print("ted se MUZES postavit")
        if pressed[pygame.K_LCTRL]:
            if self.cooldown <= 0:
                if not self.IsCrawling:  #Zmena na plazeni
                    self.CharacterSirka, self.CharacterVyska = 150, 50
                    self.GroundSpeed = 50
                    self.IsCrawling = True
                
                    self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
                    self.image.fill((255, 0, 0))
                    self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))
                
                elif self.IsCrawling and self.CanStandUp:  # Player wants to stand and has space
                    self.CharacterSirka, self.CharacterVyska = 50, 150
                    self.GroundSpeed = 250
                    self.IsCrawling = False
                
                    self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
                    self.image.fill((255, 0, 0))
                    self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))
            
                self.cooldown = 0.2
    
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
            self.vel.y = -1135 if not self.IsCrawling else -300
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
            # Gravitace ale jen pokud nelezes a nejses na zemi
            self.vel.y += 5000 * time_passed
        else:
            self.vel.y = 0

        # Updejt pozic a check kolizi pro X a Y
        self.pos.x += self.vel.x * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_x(blocks)

        self.pos.y += self.vel.y * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_y(blocks)

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

class Camera:
    def __init__(self, target, screen_width, screen_height):
        self.target = target  # Tohle je sledovanej objekt
        self.offset = pygame.math.Vector2(0, 0)
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        
        #Nastaveni kamery
        self.LERP_SPEED = 0.1
        self.DEAD_ZONE_X = 120
        self.DEAD_ZONE_Y = 200

    def lerp(self, start, end, amount):
        #pocita ten smoothnes kamery
        return start + (end - start) * amount

    def update(self):
        #Updejtuje camera posXY
        #Vypocitej target pos jako centerXaY hrace
        target_x = self.target.rect.centerx - self.SCREEN_WIDTH/2
        target_y = self.target.rect.centery - self.SCREEN_HEIGHT/2

        # Tohle dela smoothing
        self.offset.x = self.lerp(self.offset.x, target_x, self.LERP_SPEED)
        self.offset.y = self.lerp(self.offset.y, target_y, self.LERP_SPEED)

    def apply(self, entity):
        #aplikuje ofset
        return entity.rect.copy().topleft - self.offset

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

    
            #vykreslovani car to pak muzes smazat a navic se ted asi ani nevykresluji idk
            if self.CanCPlayer_Center:
                pygame.draw.line(screen, COLORS["RED"], player_bottom, enemy_top, 5)
            else:
                pygame.draw.line(screen, COLORS["GREEN"], player_bottom, enemy_top, 5)
            if self.CanCPlayer_Top:
                pygame.draw.line(screen, COLORS["RED"], player_top, enemy_top, 5)
            else:
                pygame.draw.line(screen, COLORS["GREEN"], player_top, enemy_top, 5)

            if self.CanCPlayer_Center or self.CanCPlayer_Top:
                pass
                # self.hunt()


    def killCheck(self, game_state):
        kolizeCheck = pygame.sprite.spritecollide(game_state.HracSprite.sprite, game_state.enemy_sprite, False)
        if kolizeCheck:
            print('ted ma hrac umrit')

class GameClock: #tohle je lepsi pocitadlo aby to fungovalo i kdyz hejbes s oknem
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
        
        # maximalni cap  na 0.25 funguje asi nejlip
        if delta > 0.25:  # Cap at 1/4 second
            delta = self.fixed_delta
            
        self.clock.tick(self.target_fps)
        return self.fixed_delta  

class GameState:
    def __init__(self):
        self.running = True
        self.screen = None
        self.clock = None
        self.player = None
        self.camera = None
        self.AllCaveSprites = None
        self.enemy_sprite = None
        self.game_clock = None
        self.HracSprite = None

def initPygame():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    return screen, clock

def CreateMap():
    AllCaveSprites = pygame.sprite.Group()
    
    mapp = open("map", "r")
    
    # Ground and climbing wall
    # blocks = (
    #     environmentblock(0, 540, 2280, 50),  # podlaha
    #     environmentblock(0, 0, 10, 720)      # lezecka st�na nalevo (testovaci)
    # )
    
    #prozat�m random bloky
    # for _ in range(40):
    #     x = environmentblock(random.randint(0, 2230),random.randint(300, 490), 50, 50)
    #     AllCaveSprites.add(x)
    
    for i,x in enumerate(mapp) :
        for j,y in enumerate(x) :
            if y!='2' :
                AllCaveSprites.add(environmentblock(j*75,i*75,75,75))
    
    #AllCaveSprites.add(blocks)
    return AllCaveSprites

def game_loop(game_state):
    while game_state.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
        
        #Kalkulator casu
        delta_time = game_state.game_clock.tick()
        
        # Vsechny updaty
        game_state.camera.update()
        game_state.player.update(delta_time, game_state.AllCaveSprites)
        
        enemy = game_state.enemy_sprite.sprites()[0]
        enemy.update(delta_time, game_state.AllCaveSprites)
        enemy.patrol(game_state.player, game_state.screen, game_state.AllCaveSprites)
        enemy.killCheck(game_state)
        
        #Vykreslovani - renderovani
        render_game(game_state)

def render_game(game_state):
    game_state.screen.fill(COLORS['BLACK']) #no neni to hezci v dictu
    
    #Vykresleni bloku 
    for sprite in game_state.AllCaveSprites:
        pos = game_state.camera.apply(sprite)
        game_state.screen.blit(sprite.image, pos)
    
    #Vykresleni hrace a enemy
    player = game_state.player
    enemy = game_state.enemy_sprite.sprites()[0]
    
    game_state.screen.blit(player.image, game_state.camera.apply(player))
    game_state.screen.blit(enemy.image, game_state.camera.apply(enemy))
    pygame.display.flip()

def main():
    game_state = initGame()
    game_loop(game_state)

    pygame.quit()

if __name__ == "__main__":
    main()
