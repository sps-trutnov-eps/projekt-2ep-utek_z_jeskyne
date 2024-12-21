import pygame
import random
import os, sys
import pygame_light2d as pl2d
from pygame_light2d import LightingEngine, PointLight, Hull
from pygame import draw, time
from GameOver import game_over_screen

file_dir = os.path.dirname(os.path.abspath(__file__)) #absolutni path k tomuto game_engine souboru
parent_dir = os.path.abspath(os.path.join(file_dir, os.path.pardir)) #tohle pouzije path k tomuto py soboru a jde o jeden level vys
map_file = os.path.join(parent_dir, "map")
difficulty_file = os.path.join(file_dir, "diff")
Enemy_Texture = os.path.join(parent_dir, "Textury", "Enemy02.png")
PLayer_Texture = os.path.join(parent_dir, "Textury", "Character01.png")
Kamen1_Texture = os.path.join(parent_dir, "Textury", "Kamen01.png")
Kamen2_Texture = os.path.join(parent_dir, "Textury", "Kamen02.png")
Dum_Texture = os.path.join(parent_dir, "Textury", "Domecek01.png")
Lopata_texture = os.path.join(parent_dir, "Textury", "Lopata01.png")

try:
    with open(difficulty_file, "r") as file:
        difficulty = int(file.read().strip())
        print("It hecking works")
except FileNotFoundError:
    print("Error: Difficulty file not found. Using random difficulty.")
    difficulty = random.randint(1,3)
except ValueError:
    print("Error: Invalid difficulty value in the file. Using random difficulty.")
    difficulty = random.randint(1,3)


pygame.init()
screen = pygame.display.set_mode((1280, 720))

lights_engine = LightingEngine(
    screen_res=(1280, 720),  # Replace with your screen width and height
    native_res=(1280, 720),  # Often same as screen resolution
    lightmap_res=(1280, 720)  # Often same as screen resolution
)

COLORS = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255)
}

def initGame(difficulty):
    game_state = GameState()
    
    # init pygame
    pygame.init()
    
    # init obrazovku a hodiny
    game_state.screen = pygame.display.get_surface()
    game_state.clock = pygame.time.Clock()
    
    # HRAC vytvoreni
    game_state.player = character(0, 100, 100, OnGround = True, CharacterSirka = 50, CharacterVyska = 150)
    
    #Sprite Hrace
    game_state.HracSprite = pygame.sprite.GroupSingle()
    game_state.HracSprite.add(game_state.player) 
    
    #inicializace svicky a svetla
    game_state.Candle = Candle(game_state.player.rect.centerx, game_state.player.rect.centery)
        
    game_state.Light = Light(game_state.player.rect.centerx, game_state.player.rect.centery)

    #Inicializace Kamery
    game_state.camera = Camera(game_state.player, 1280, 720)
    
    #Postav mapu, upec chleba
    game_state.CaveRockSprites, game_state.CaveBackgroundSprites = CreateMap()
   
    #Enemy init, podle difficulty
    game_state.enemy_sprite = pygame.sprite.Group()
    random_spawn_points = []
    
    #Projede veskery mozny spawn pointy
    #uz je to tady i pro lopatu
    with open(map_file, "r") as map:
        for i, x in enumerate(map):
            for j, y in enumerate(x.strip()):
                if y == '2':
                    random_spawn_points.append((j*75, i*75))
    print(difficulty)
    #Spawn pocet podle difficulty na random mista
    for i in range(difficulty):
        if random_spawn_points:
            spawn_point = random.choice(random_spawn_points)
            enemy = Enemy(spawn_point[0], spawn_point[1], True)
            game_state.enemy_sprite.add(enemy)
            random_spawn_points.remove(spawn_point)
    
    #lopata
    shovel_spawn_point = random.choice(random_spawn_points)
    #game_state.lopata = Shovel(shovel_spawn_point[0], shovel_spawn_point[1])  #Spawn lopatu na vybrany volny random misto
    game_state.lopata = Shovel(0, -75)
    game_state.shovel_sprite = pygame.sprite.GroupSingle()  #bude jen jedna lopata
    game_state.shovel_sprite.add(game_state.lopata)  # Add to sprite group
   
    
    #inicializuj gameclock, kterej se jen stara o to abys mohl hejbat s oknem a nepokazilo to timing
    game_state.game_clock = GameClock(60)
    
    return game_state

class GameFinish:
    def __init__(self, x, y):
        self.Image = pygame.image.load(Dum_Texture).convert_alpha()
        self.x = x
        self.y = y
        self.rect = self.Image.get_rect(topleft=(x, y))

    def Spawn():
        pass
    #jen at to vezme pocet bloku v prvni rade a vynasobi to 75 a pak to spawne na ty souradnici
    
    def CheckEndGame(self, Hrac):
        if self.rect.colliderect(Hrac.rect):
            print("Game END, you escaped")
            return True
        return False

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

class Shovel(pygame.sprite.Sprite):
    def __init__(self, posX, posY):
        super().__init__()
        self.posX = posX
        self.posY = posY
        self.image = pygame.image.load(Lopata_texture).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.texture = lights_engine.surface_to_texture(self.image)
        self.rect = self.image.get_rect(topleft=(self.posX, self.posY))
        self.durability = 7
        self.is_held = False
        self.is_active = False

    def update(self, player):
        if not self.is_held and self.rect.colliderect(player.rect):
            self.is_held = True
            return True
        return False


    def destroyWalls(self, Rock, BackgRock, player, camera):
        if not self.is_held or self.durability <= 0:
            return False

        mouse_pos = pygame.mouse.get_pos()
        camera_offset = (camera.offset.x, camera.offset.y)
        # Adjust for the camera's offset to get the real-world position
        mouse_rect = pygame.Rect(mouse_pos[0] + camera_offset[0], mouse_pos[1] + camera_offset[1], 1, 1)

        destroyed_blocks = []
        if self.is_held and pygame.mouse.get_pressed()[0]:  # Check if the left mouse button is clicked
            for block in Rock:
                if mouse_rect.colliderect(block.rect):
                    # Move block from Rock to BackgRock
                    new_background_block = environmentblock(
                        block.rect.x, block.rect.y, block.rect.width, block.rect.height
                    )
                    new_background_block.image1 = block.image1  # Preserve the original texture
                    BackgRock.add(new_background_block)
                    destroyed_blocks.append(block)

                    # Reduce durability for each destroyed block
                    self.durability -= 1
                    if self.durability <= 0:
                        break

        # Remove destroyed blocks from the Rock group
        for block in destroyed_blocks:
            Rock.remove(block)

        return len(destroyed_blocks) > 0
       
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
        self.original_surface = pygame.image.load(PLayer_Texture)
        
        # Create standing and crawling surfaces with proper dimensions
        self.standing_surface = pygame.transform.scale(self.original_surface, (75, 150))
        self.crawling_surface = pygame.transform.scale(self.original_surface, (75, 75)) #lmao udelej z nej ctverec a vleze se vsude
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
                self.CharacterSirka, self.CharacterVyska = 75, 75
                self.GroundSpeed = 125
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
                self.CharacterSirka, self.CharacterVyska = 75, 150
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
            self.vel.y = -1135 if not self.IsCrawling else -1135#skakani nelze behem krceni
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
            position=(x,y),        #souradnice x, y
            power = 3,            # Default power
            radius = 300,         #
        )
        self.head_light.set_color(255,100,0, 255)
        lights_engine.lights.append(self.head_light)

    def createSource(self, player, camera_offset):
        #hlavova pozice na vrchu hrace
        head_x = float(player.rect.centerx - camera_offset[0])
        head_y = float(player.rect.top - camera_offset[1])

        # Update the head light position
        self.head_light.position = (head_x, head_y)

class Candle:
    def __init__(self, x, y):
        self.source = [x,y]
        self.particles = []      # [location, velocity, timer]
        self.cooldown = 0

    def circleSurface(self, radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        texture = lights_engine.surface_to_texture(surf)
        return texture

    def createSourceCandle(self, player, screen, camera_offset):
        PosHrac = [player.rect.centerx, player.rect.centery]

        self.cooldown += 1
        #                                   pos      random pohyb do stran      pohyb nahoru    jak budou velky, postupne se zmensujou
        if self.cooldown > 3:
            self.particles.append([[PosHrac[0], PosHrac[1]], [random.uniform(-0.5, 0.5), -1.8], random.randint(2, 3)])
            self.cooldown = 0

        for particle in self.particles:
            particle[0][0] += particle[1][0] #pohyb do stran
            particle[0][1] += particle[1][1] #pohyb nahoru
            particle[1][1] += 0.004 #to je pohyb nahoru
            particle[2] -= 0.03  #to je zmensuje
            if particle[2] > 0:
                radius = int(particle[2] * 4)
                light_surf = self.circleSurface(radius, (255, 193, 0))
                if radius > 0:
                    lights_engine.render_texture(
                                    light_surf,  #textura tvorena v circlesurface
                                    pl2d.BACKGROUND,  #Foreground znamena ze neni afektovana svetlem
                                    pygame.Rect(particle[0][0] - camera_offset[0] - radius, particle[0][1] - camera_offset[1] - radius - 70, radius * 2, radius * 2),  # Destination rect
                                    pygame.Rect(0, 0, radius * 2, radius * 2)  # Source rect
                                )
                    light_surf.release()
            else:
                self.particles.remove(particle)

class environmentblock(pygame.sprite.Sprite):
    def __init__(self, x, y, sirka, vyska, is_background=True):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.sirka = sirka
        self.vyska = vyska
        self.image = pygame.Surface((self.sirka, self.vyska))
        self.image.fill((255, 255, 255)) 
       
        # Load the original image as a Pygame surface first to get dimensions
        self.original_surface1 = pygame.image.load(Kamen1_Texture) #svetly kamen
        self.original_surface2 = pygame.image.load(Kamen2_Texture) #bedrock
        
        # Create normal surfaces with proper dimensions
        self.normal_surface1 = pygame.transform.scale(self.original_surface1, (75, 75))
        self.normal_surface2 = pygame.transform.scale(self.original_surface2, (75, 75))
        
        # Convert surfaces to textures
        self.NormalImage1 = lights_engine.surface_to_texture(self.normal_surface1)
        self.NormalImage2 = lights_engine.surface_to_texture(self.normal_surface2)
        
        # Set initial image and create rect with correct dimensions
         # Keep track of current surface for dimensions
        self.image1 = self.NormalImage1  # Current texture for rendering
        self.rect = pygame.Rect(
            round(self.pos.x),
            round(self.pos.y),
            self.normal_surface1.get_width(),
            self.normal_surface1.get_height()
        )
        self.image2 = self.NormalImage2  # Current texture for rendering
        self.rect = pygame.Rect(
            round(self.pos.x),
            round(self.pos.y),
            self.normal_surface2.get_width(),
            self.normal_surface2.get_height()
        )

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, OnGround):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.move = pygame.math.Vector2(200, 0)  #pocatecni rychlost x, jde doprava
        self.OnGround = OnGround
        self.image = pygame.Surface((74, 74))
        self.image.fill((200, 0, 200))
        self.rect = self.image.get_rect(topleft = (round(self.pos.x), round(self.pos.y)))
        self.Speed = 200  #Rychlost pohybu
        self.CanCPlayer = False # Can see player
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
        self.original_surface = pygame.image.load(Enemy_Texture)
        self.standing_surface = pygame.transform.scale(self.original_surface, (75, 45))
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

    def patrol(self, Hrac, CaveRockSprites, time_passed):
        if self.isHunting: #pokud lovi, spust hunt :)
            self.hunt(Hrac, CaveRockSprites, time_passed)
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

        self.check_player_visibility(Hrac, CaveRockSprites)

    def check_player_visibility(self, Hrac, CaveRockSprites):

        #Tohle vsechno jen checkuje jestli vidi hrace
        #A kouka jednou na nohy a jednou na hlavu, protoze mi to prislo lepsi
        player_bottom = (Hrac.rect.center[0], Hrac.rect.bottom - 10)
        player_top = (Hrac.rect.center[0], Hrac.rect.top + 10)
        enemy_top = (self.rect.center[0], self.rect.top + 20)

        self.CanCPlayer = True

        distanceToPlayer = self.pos.distance_to(Hrac.pos)

        #checkujes jestli nevidi hrace
        for block in CaveRockSprites:
            if block.rect.clipline(player_bottom, enemy_top) or block.rect.clipline(player_top, enemy_top):
                self.CanCPlayer = False
                break

        # Start huntu pokud vidi hrace a je dost blizko
        if self.CanCPlayer and distanceToPlayer < self.huntRange and self.huntCooldown <= 0:
            self.isHunting = True


    def hunt(self, Hrac, CaveRockSprites, time_passed):
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
        self.CaveRockSprites = None
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
    CaveRockSprites = pygame.sprite.Group()
    CaveBackgroundSprites = pygame.sprite.Group()
    
    with open(map_file, "r") as mapp:
        lines = mapp.readlines()

    with open(map_file, "r") as mapp:
        for i, x in enumerate(mapp):
            for j, y in enumerate(x.strip()):
                CaveBackgroundSprites.add(environmentblock(j*75, i*75, 75, 75))
                if y == '1' or y == '0':
                    CaveRockSprites.add(environmentblock(j*75, i*75, 75, 75))


    return CaveRockSprites, CaveBackgroundSprites

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
        game_state.player.update(delta_time, game_state.CaveRockSprites)

        for enemy in game_state.enemy_sprite.sprites():
            enemy.update(delta_time, game_state.CaveRockSprites)
            enemy.patrol(game_state.player, game_state.CaveRockSprites, game_state.time_passed)
            enemy.killCheck(game_state)

        
        game_state.lopata.update(game_state.player)
        game_state.lopata.destroyWalls(game_state.CaveRockSprites,game_state.CaveBackgroundSprites, game_state.player, game_state.camera)

        #Vykreslovani - renderovani
        render_game(game_state)

def render_game(game_state):
    # Clear the lighting engine surface
    lights_engine.clear(0, 0, 0, 255)
    
    #Vykresleni bloku 
    for sprite in game_state.CaveBackgroundSprites:
        pos = game_state.camera.apply(sprite)
        if pos[0] > -75 and pos[0]<1280 and pos[1]>-75 and pos[1] <720:
            # musis pridat destinaci a zdroj kazdymu rectu
            # Convert tuples to pygame.Rect objects
            dest_rect = pygame.Rect(pos[0], pos[1], sprite.rect.width, sprite.rect.height)
            source_rect = pygame.Rect(0, 0, sprite.rect.width, sprite.rect.height)
            lights_engine.render_texture(sprite.NormalImage2, pl2d.BACKGROUND, dest_rect, source_rect)

    
    # Render rock sprites on top of background
    for sprite in game_state.CaveRockSprites:
        pos = game_state.camera.apply(sprite)
        if pos[0] > -75 and pos[0] < 1280 and pos[1] > -75 and pos[1] < 720:
            dest_rect = pygame.Rect(pos[0], pos[1], sprite.rect.width, sprite.rect.height)
            source_rect = pygame.Rect(0, 0, sprite.rect.width, sprite.rect.height)
            lights_engine.render_texture(sprite.NormalImage1, pl2d.BACKGROUND, dest_rect, source_rect)

    
    camera_offset = (game_state.camera.offset.x, game_state.camera.offset.y)

    # hrac se vsema nalezitostma (rect)
    player = game_state.player
    player_pos = game_state.camera.apply(player)
    player_dest = pygame.Rect(player_pos[0], player_pos[1], player.rect.width, player.rect.height)
    player_source = pygame.Rect(0, 0, player.rect.width, player.rect.height)
    lights_engine.render_texture(player.image, pl2d.BACKGROUND, player_dest, player_source)

    #render enemy se spravnejma rectama
    for enemy in game_state.enemy_sprite.sprites():
        enemy_pos = game_state.camera.apply(enemy)
        enemy_dest = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy.rect.width, enemy.rect.height)
        enemy_source = pygame.Rect(0, 0, enemy.rect.width, enemy.rect.height)
        lights_engine.render_texture(enemy.image, pl2d.BACKGROUND, enemy_dest, enemy_source)
    

    #A lopata at last
    shovel = game_state.lopata
    shovel_pos = game_state.camera.apply(shovel)
    shovel_dest = pygame.Rect(shovel_pos[0], shovel_pos[1], shovel.image.get_width(), shovel.image.get_height())
    shovel_source = pygame.Rect(0, 0, shovel.image.get_width(), shovel.image.get_height())
    lights_engine.render_texture(shovel.texture, pl2d.BACKGROUND, shovel_dest, shovel_source)


    #vykresleni svetla - candle
    game_state.Candle.createSourceCandle(game_state.player, game_state.screen, camera_offset)

    game_state.Light.createSource(game_state.player, camera_offset)

    lights_engine.render()

    pygame.display.flip()

def main(difficulty):
    game_state = initGame(difficulty)
    game_loop(game_state)

    pygame.quit()

if __name__ == "__main__":
    difficulty = random.randint(1,3)
    main(difficulty)
