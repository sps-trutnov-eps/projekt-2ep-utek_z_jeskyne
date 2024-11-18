import pygame
import random
import pygame_light2d as pl2d
from pygame_light2d import LightingEngine, PointLight, Hull
from pygame.locals import *
from pygame import time
from GameOver import game_over_screen
pygame.init()

# Screen resolution and lighting engine setup
screen_res = (1280, 720)
lights_engine = LightingEngine(
    screen_res=screen_res, native_res=screen_res, lightmap_res=(int(screen_res[0]/2.5), int(screen_res[1]/2.5)))

# Set ambient light
lights_engine.set_ambient(15, 15, 15, 255) #tohle dela "tmu" r, g, b, -
# Add initial hull
vertices = [(125, 50), (200, 50), (200, 125), (125, 125)]
hull = Hull(vertices)
lights_engine.hulls.append(hull)

# Add a point light - use default coordinates
head_light = PointLight(
    screen_res[0] // 2,  # x coordinate (center of screen)
    screen_res[1] // 2,  # y coordinate (center of screen)
    150,  # radius
    (255, 193, 0, 255)  # Warm light color (R,G,B,A)
)


lights_engine.lights.append(head_light)
COLORS = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255)
}

def initGame():
    game_state = GameState()
    
    # init Pygame without setting display mode
    pygame.init()
    
    # init screen and clock
    game_state.screen = pygame.display.set_mode(screen_res, pygame.OPENGL | pygame.DOUBLEBUF) #bitwise or = |
    game_state.clock = pygame.time.Clock()
    
    # HRAC vytvoreni
    game_state.player = character(1000, 100, 100, OnGround = True, CharacterSirka = 50, CharacterVyska = 150)
    
    #Sprite Hrace
    game_state.HracSprite = pygame.sprite.GroupSingle()
    game_state.HracSprite.add(game_state.player) 
    
    #inicializace svetla
    game_state.Light = Light(game_state.player.rect.centerx, game_state.player.rect.centery)

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

        #staty a stavy
        self.cooldown = 0   #Cooldown mezi zmenenim stavu (stani/plazeni)
        self.GroundSpeed = 250  #rychlost pohybu normalne
        self.ClimbSpeed = 100
        self.CanStandUp = True
        self.IsCrawling = False
        self.IsCrawling = False
        self.IsClimbing = False
        self.DivaSeDoprava = True


        # Load the original image as a Pygame surface first to get dimensions
        self.original_surface = pygame.image.load("Character01.png")
        
        # Create standing and crawling surfaces with proper dimensions
        self.standing_surface = pygame.transform.scale(self.original_surface, (70, 150))
        self.crawling_surface = pygame.transform.scale(self.original_surface, (150, 70))
        self.flipped_surface = pygame.transform.flip(self.standing_surface, True, False)
        
        # Convert surfaces to textures
        self.StandingImage = lights_engine.surface_to_texture(self.standing_surface)
        self.CrawlingImage = lights_engine.surface_to_texture(self.crawling_surface)
        self.FlippedImage = lights_engine.surface_to_texture(self.flipped_surface)

        #soucasny vyska,sirka pro zmenu crawling/standing
        self.current_width = self.standing_surface.get_width()
        self.current_height = self.standing_surface.get_height()
        
        # Set initial image and create rect with correct dimensions
        self.current_surface = self.standing_surface  # Keep track of current surface for dimensions
        self.image = self.StandingImage  # Current texture for rendering
        self.rect = pygame.Rect(
            round(self.pos.x), 
            round(self.pos.y),
            self.current_surface.get_width(),
            self.current_surface.get_height()
        )

    def update_rect_dimensions(self, width, height, pos_x, pos_y):
        #updatuje sirku vysku s origo rectama
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx
        self.rect = pygame.Rect(
            round(pos_x),
            round(pos_y),
            width,
            height
        )
        self.rect.bottom = old_bottom
        self.rect.centerx = old_centerx

    def update(self, time_passed, blocks):
        self.CanStandUp = True
        pressed = pygame.key.get_pressed()
        #tohle je blok nad hracem, pres kterej se kontroluje jestli se muze postavit
        SpaceCheckerRect = pygame.Rect(self.rect.x + 50, self.rect.y - (100 - self.CharacterVyska), 50, 50)
        
        for block in blocks:
            if SpaceCheckerRect.colliderect(block.rect):
                self.CanStandUp = False
                break
        #Tohle handeluje zmenu mezi stanim a plazenim i s texturama
        if pressed[pygame.K_LCTRL] and self.cooldown <= 0:
            if not self.IsCrawling:  #Zmeni se na plazeni
                self.CharacterSirka, self.CharacterVyska = 150, 50
                self.GroundSpeed = 70
                self.IsCrawling = True
                #Textura handeling
                self.image = self.CrawlingImage #nastavi image na resizenuty image
                self.current_width = self.crawling_surface.get_width()
                self.current_height = self.crawling_surface.get_height()
                self.update_rect_dimensions(
                    self.current_width,
                    self.current_height,
                    self.pos.x,
                    self.pos.y
                ) 
            elif self.IsCrawling and self.CanStandUp:  #Zmena na postaveni, pokud ma nad sebou misto
                self.CharacterSirka, self.CharacterVyska = 50, 150
                self.GroundSpeed = 250
                self.IsCrawling = False
                #Textura handeling, stejne jako vyse
                self.current_width = self.standing_surface.get_width()
                self.current_height = self.standing_surface.get_height()
                self.update_rect_dimensions(
                    self.current_width,
                    self.current_height,
                    self.pos.x,
                    self.pos.y
                )
            self.cooldown = 0.2

        if self.cooldown > 0:
            self.cooldown -= time_passed 


        # Horizontalni movement
        self.vel.x = 0
        if pressed[pygame.K_LEFT]:# or pressed[pygame.K_a]:
            self.vel.x -= self.GroundSpeed
            if self.DivaSeDoprava: #pokud se divas doprava tak se otoci image
                CurrentImage = self.StandingImage if not self.IsCrawling else self.CrawlingImage #check jestli ma byt postava na vysku nebo sirku
                self.image = self.FlippedImage #otoceni image (prvni bool je osa X, druhy Y)
                self.DivaSeDoprava = False #uz se nediva doprava
        if pressed[pygame.K_RIGHT]:# or pressed[pygame.K_d]:
            self.vel.x += self.GroundSpeed
            if not self.DivaSeDoprava: #stejny co vyse
                CurrentImage = self.StandingImage if not self.IsCrawling else self.CrawlingImage
                self.image = CurrentImage #tady se ale pouzije origo image
                self.DivaSeDoprava = True

        # Skakani
        if pressed[pygame.K_UP] and self.OnGround and not self.IsClimbing:
            self.vel.y = -1135 if not self.IsCrawling else 0 #tady nevim, asi odstranit skakani na zemi uplne?
            self.OnGround = False  #Nastavi okamzite ze nejsi na zemi

        #lezeni
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


class Light:
    def __init__(self, x, y):
        self.head_light = PointLight(
            x, y,  # Use actual x, y coordinates
            150,  # radius
            (255, 193, 0, 255)  # Warm light color (R,G,B,A)
        )
        lights_engine.lights.append(self.head_light)

    def circleSurface(self, radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def createSource(self, player, camera_offset):
        print(f"Camera offset: {camera_offset}, Type: {type(camera_offset)}")
        # Calculate head position (slightly above character center)
        head_x = player.rect.centerx - camera_offset[0]
        head_y = player.rect.top - camera_offset[1] + 20  # Offset from top of character
        
        # Update the point light position to follow the head
        self.head_light.x = head_x
        self.head_light.y = head_y

        # Particle effects for additional atmosphere
        self.cooldown += 1
        if self.cooldown > 3:
            self.particles.append([
                [head_x, head_y],  # Start particles from head position
                [random.uniform(-0.5, 0.5), -1.8], 
                random.randint(2, 3)
            ])
            self.cooldown = 0

        # Update existing particles
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[1][1] += 0.004
            particle[2] -= 0.03
            
            if particle[2] > 0:
                radius = int(particle[2] * 4)
                light_surf = self.circleSurface(radius, (255, 193, 0))
            else:
                self.particles.remove(particle)
        

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

        #####################################################################################################################
        # Load the original image as a Pygame surface first to get dimensions
        self.original_surface = pygame.image.load("Kamen01.png")
        
        # Create normal surfaces with proper dimensions
        self.standing_surface = pygame.transform.scale(self.original_surface, (75, 75))
        
        # Convert surfaces to textures
        self.NormalImage = lights_engine.surface_to_texture(self.standing_surface)
        
        # Set initial image and create rect with correct dimensions
        self.current_surface = self.standing_surface  # Keep track of current surface for dimensions
        self.image = self.NormalImage  # Current texture for rendering
        self.rect = pygame.Rect(
            round(self.pos.x), 
            round(self.pos.y),
            self.current_surface.get_width(),
            self.current_surface.get_height()
        )


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
        self.DivaSeDoprava = False

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


        # Load and prepare both normal and flipped textures at initialization
        self.original_surface = pygame.image.load("Enemy01.png")
        self.standing_surface = pygame.transform.scale(self.original_surface, (300, 100))
        self.flipped_surface = pygame.transform.flip(self.standing_surface, True, False)
        
        # Convert surfaces to textures
        self.StandingImage = lights_engine.surface_to_texture(self.standing_surface)
        self.FlippedImage = lights_engine.surface_to_texture(self.flipped_surface)
        
        # Set initial image and create rect with correct dimensions
        self.current_surface = self.standing_surface  # Keep track of current surface for dimensions
        self.image = self.StandingImage  # Current texture for rendering
        self.rect = pygame.Rect(
            round(self.pos.x), 
            round(self.pos.y),
            self.current_surface.get_width(),
            self.current_surface.get_height()
        )

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
            self.image = self.FlippedImage
            self.DivaSeDoprava = True  #uz se diva doprava
        elif self.move.x < 0 and self.DivaSeDoprava:
            self.image = self.StandingImage
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
        #vraci pevnou deltu casu
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
    # Clear the lighting engine surface
    lights_engine.clear(0, 0, 0, 255)
    
    #Vykresleni bloku 
    for sprite in game_state.AllCaveSprites:
        pos = game_state.camera.apply(sprite)
        if pos[0] > -75 and pos[0]<1280 and pos[1]>-75 and pos[1] <720:
            # musis pridat destinaci a zdroj kazdymu rectu
            # Convert tuples to pygame.Rect objects
            dest_rect = pygame.Rect(pos[0], pos[1], sprite.rect.width, sprite.rect.height)
            source_rect = pygame.Rect(0, 0, sprite.rect.width, sprite.rect.height)
            lights_engine.render_texture(sprite.NormalImage, pl2d.BACKGROUND, dest_rect, source_rect)

    
    camera_offset = (game_state.camera.offset.x, game_state.camera.offset.y) #pro svetlo na svicce

    #Vykresleni hrace a enemy
    player = game_state.player
    enemy = game_state.enemy_sprite.sprites()[0]


    # hrac se vsema nalezitostma (rect)
    player_pos = game_state.camera.apply(player)
    player_dest = pygame.Rect(player_pos[0], player_pos[1], player.rect.width, player.rect.height)
    player_source = pygame.Rect(0, 0, player.rect.width, player.rect.height)
    lights_engine.render_texture(player.image, pl2d.BACKGROUND, player_dest, player_source)

    #render enemy se spravnejma rectama
    enemy_pos = game_state.camera.apply(enemy)
    enemy_dest = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy.rect.width, enemy.rect.height)
    enemy_source = pygame.Rect(0, 0, enemy.rect.width, enemy.rect.height)
    lights_engine.render_texture(enemy.image, pl2d.BACKGROUND, enemy_dest, enemy_source)

    #vykresleni svetla na svicce
    game_state.Light.createSource(game_state.player, camera_offset)
    
    # Render lights
    lights_engine.render()
    

    pygame.display.flip()

def main():
    game_state = initGame()
    game_loop(game_state)

    pygame.quit()

if __name__ == "__main__":
    main()
