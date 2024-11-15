import pygame
from pygame import time
from GameOver import game_over_screen
import math
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
    
    # init Pygame
    game_state.screen, game_state.clock = initPygame()
    
    # HRAC vytvoreni
    game_state.player = character(1000, 100, 100, OnGround = True, CharacterSirka = 50, CharacterVyska = 150)
    
    #Sprite Hrace
    game_state.HracSprite = pygame.sprite.GroupSingle()
    game_state.HracSprite.add(game_state.player) 
    
    #Inicializace Kamery
    game_state.camera = Camera(game_state.player, 1280, 720)
    
    #Postav mapu, upec chleba
    game_state.AllCaveSprites = CreateMap()
    
    #Enemy init, pozdejc jich mozna bude vic
    enemy = Enemy(300, 0, True)
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

        #puvodni obrazek
        self.OriginalImage = pygame.image.load("Character01.png").convert_alpha()
        #load textury a resize pro lezeni a stani
        self.StandingImage = pygame.transform.scale(self.OriginalImage, (70, 150))
        self.CrawlingImage = pygame.transform.rotate(self.OriginalImage, -90)
        self.CrawlingImage = pygame.transform.scale(self.CrawlingImage, (150, 70))

        #Toto je zacatecni image
        self.image = self.StandingImage
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))

        #staty a stavy
        self.cooldown = 0   #Cooldown mezi zmenenim stavu (stani/plazeni)
        self.GroundSpeed = 250  #rychlost pohybu normalne
        self.ClimbSpeed = 100
        self.CanStandUp = True
        self.IsCrawling = False
        self.IsCrawling = False
        self.IsClimbing = False
        self.DivaSeDoprava = True
    def n_choose_k(n,k) :
        return math.factorial(n)/(math.factorial(k) * math.factorial(n - k))
    def cub_blezier(vec, x) :
        e = 0
        for i in range(4) :
            e+=n_choose_k(4,i)*(1-x)**(4-i)*x**i*vec[i]
        return e
    def update() :
        pass
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
        self.OriginalImage = pygame.image.load("Kamen01.png")
        self.TextureImage = pygame.transform.scale(self.OriginalImage, (75, 75))
        self.rect = self.image.get_rect(topleft=(round(self.pos.x), round(self.pos.y)))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, OnGround):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.move = pygame.math.Vector2(200, 0)  #pocatecni rychlost x, jde doprava
        self.OnGround = OnGround
        self.image = pygame.Surface((150, 50))
        self.image.fill((200, 0, 200))
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))
        self.Speed = 200  #Rychlost pohybu
        self.CanCPlayer = False # Can see ((c -> [sí] = see)) player
        self.DivaSeDoprava = True

        # Patrol parametry
        self.patrolStart = x #Pocatecni pozice patrolu, rovna se enemy spawnu
        self.basePatrolRange = 300  # Pocatecni hodnota
        self.maxPatrolRange = 2000  # Max Vzdalenost kam az dojde behem sveho hledani Hrace, postupne se bude zvetsovat treba (momentalne je mapa 3940 jednotek siroka)
        self.currentPatrolRange = self.basePatrolRange  # Soucasne nastaveni patrolu
        self.patrolDirection = 1 #haha 1Direction
        self.patrolCycles = 0  # Pocitacka cyklu (protoze chodi tam a zpet)
        self.expandRange = True  # Jestli ma na dalsim cyklu jit dal
        
        # Hunt parametry
        self.huntCooldown = 0
        self.huntSpeed = 300  # Rychlejsi nez hrac kdyz lovi
        self.huntRange = 400  # Vzdalenost na jakou detekuje hrace
        self.isHunting = False
        
        # skakani
        self.jumpForce = -1000 #stejne jako hrac
        self.jumpCooldown = 0
        self.maxJumpCooldown = 1.0  # 1 sekunda cooldown
        self.jumping = False

        #nacteni a nastaveni textury spritu
        self.OriginalImage = pygame.image.load("Enemy01.png").convert_alpha()
        self.StandingImage = pygame.transform.scale(self.OriginalImage, (300, 100))
        self.image = self.StandingImage
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))

    def update(self, time_passed, blocks):
        #skok schlazeniodpocet updejt
        if self.jumpCooldown > 0:
            self.jumpCooldown -= time_passed

        #gravitace
        self.move.y += 5000 * time_passed

        self.OnGround = False

        if self.huntCooldown > 0:
            self.huntCooldown -= time_passed

        # Update kolizi a update pozice
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_x(blocks)

        self.pos.y += self.move.y * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.check_collisions_y(blocks)

        #Skakani spoustene pres funkci check_collisions_x(blocks)
        if self.jumping and self.OnGround and self.jumpCooldown <= 0:
            self.move.y = self.jumpForce
            self.jumpCooldown = self.maxJumpCooldown
            self.jumping = False

        #flipovani textury
        if self.move.x > 0 and not self.DivaSeDoprava: #pohyb doprava
            self.image = pygame.transform.flip(self.StandingImage, True, False) #otoceni image (prvni bool je osa X, druhy Y)
            self.DivaSeDoprava = True  #uz se diva doprava
        elif self.move.x < 0 and self.DivaSeDoprava:
            self.image = self.StandingImage  #tady se ale pouzije origo image
            self.DivaSeDoprava = False

    def patrol(self, Hrac, AllCaveSprites, time_passed):
        if self.isHunting: #pokud lovi, spust hunt :)
            self.hunt(Hrac, AllCaveSprites, time_passed)
            return


        #Pohyb nepritele podle patrolu
        self.move.x = self.Speed * self.patrolDirection
        self.pos.x += self.move.x * time_passed
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        
        #Kdyz se dostane na kraj svyho patrol range tak se otoci
        #TODO: zatim neresi ze se muze zaseknout 
        distance_from_start = abs(round(self.pos.x) - self.patrolStart)
        if distance_from_start >= self.currentPatrolRange:
            self.patrolDirection *= -1  #otocka
            self.patrolCycles += 1

        #kazde 2 cykly tj. tam a zpet se prida range
            if self.patrolCycles % 2 == 0 and self.expandRange:
                self.currentPatrolRange = min(self.currentPatrolRange + 400, self.maxPatrolRange)
                self.expandRange = False
            else:
                self.expandRange = True

        self.check_player_visibility(Hrac, AllCaveSprites)

    def check_player_visibility(self, Hrac, AllCaveSprites):

        #Tohle vsechno jen checkuje jestli vidi hrace
        #A kouka jednou na nohy a jednou na hlavu, protoze mi to prislo lepsi
        player_bottom = (Hrac.rect.center[0], Hrac.rect.bottom - 10)
        player_top = (Hrac.rect.center[0], Hrac.rect.top + 10)
        enemy_top = (self.rect.center[0], self.rect.top + 20)

        self.CanCPlayer = True

        distanceToPlayer = self.pos.distance_to(Hrac.pos)

        #checkujes jestli nevidi hrace
        for block in AllCaveSprites:
            if block.rect.clipline(player_bottom, enemy_top) or block.rect.clipline(player_top, enemy_top):
                self.CanCPlayer = False
                break

        # Start huntu pokud vidi hrace a je dost blizko
        if self.CanCPlayer and distanceToPlayer < self.huntRange and self.huntCooldown <= 0:
            self.isHunting = True


    def hunt(self, Hrac, AllCaveSprites, time_passed):
        distance = self.pos.distance_to(Hrac.pos)

        #Pokud je hrac moc daleko, vrati se zpet k patrolu
        if distance > self.huntRange * 1.3:  #Trosku vic range nez se vzda
            self.isHunting = False
            self.huntCooldown = 2.0  # 2 sekundy cooldown nez muze zase ĺovit
            return

        # Pohyb smerem k hraci
        direction = 1 if Hrac.pos.x > self.pos.x else -1 
        self.move.x = self.huntSpeed * direction
        self.pos.x += self.move.x * time_passed
        
        #Jakmile se dostane blizko, game over
        if distance < 20:
            game_over_screen()


    def check_collisions_x(self, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.OnGround:
                    self.jumping = True
                if self.move.x > 0:  # pohybuje se doprava
                    self.rect.right = block.rect.left
                elif self.move.x < 0:  # pohyb doleva
                    self.rect.left = block.rect.right
                self.pos.x = self.rect.midbottom[0]
                    

    def check_collisions_y(self, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.move.y > 0:  # padani
                    self.rect.bottom = block.rect.top
                    self.move.y = 0
                    self.OnGround = True
                elif self.move.y < 0:  # skakani
                    self.rect.top = block.rect.bottom
                    self.move.y = 0
                self.pos.y = self.rect.midbottom[1]


    def killCheck(self, game_state):
        kolizeCheck = pygame.sprite.spritecollide(game_state.HracSprite.sprite, game_state.enemy_sprite, False)
        if kolizeCheck:
            print('Umrels, prohrals!')
            game_over_screen()

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
        
        # maximalni cap  na 0.25 funguje nejlip
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
        self.time_passed = None

def initPygame():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    return screen, clock

def CreateMap():
    AllCaveSprites = pygame.sprite.Group()
    
    mapp = open("map", "r")

    for i,x in enumerate(mapp) :
        for j,y in enumerate(x) :
            if y!='2' :
                AllCaveSprites.add(environmentblock(j*75,i*75,75,75))

    return AllCaveSprites

def game_loop(game_state):
    while game_state.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
        
        #Kalkulator ubehleho casu
        delta_time = game_state.game_clock.tick()
        game_state.time_passed = delta_time 
        
        # Vsechny updaty
        game_state.camera.update()
        game_state.player.update(delta_time, game_state.AllCaveSprites)
        
        enemy = game_state.enemy_sprite.sprites()[0]
        enemy.update(delta_time, game_state.AllCaveSprites)
        enemy.patrol(game_state.player, game_state.AllCaveSprites, game_state.time_passed)
        enemy.killCheck(game_state)
        
        #Vykreslovani - renderovani
        render_game(game_state)

def render_game(game_state):
    game_state.screen.fill(COLORS['BLACK']) #no neni to hezci v dictu
    
    #Vykresleni bloku 
    for sprite in game_state.AllCaveSprites:
        pos = game_state.camera.apply(sprite)
        if pos[0] > -75 and pos[0]<1280 and pos[1]>-75 and pos[1] <720 :
            #game_state.screen.blit(sprite.image, pos)
            game_state.screen.blit(sprite.TextureImage, pos)
    
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
