import pygame
from pygame import key


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True



class character(pygame.sprite.Sprite):
	def __init__(self, x, y, HP, OnGround, CharacterSirka, CharacterVyska):
		super().__init__()
		self.pos = pygame.math.Vector2(x, y)
		self.move = pygame.math.Vector2()
		self.HP = HP
		self.OnGround = OnGround
#		self.image = pygame.image.load('character.png').convert_alpha()
		self.image = pygame.Surface((CharacterSirka, CharacterVyska))
		self.image.fill((255, 0, 0)) 
		self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))
		self.Zet = 1 #pro potreby zmeny Postavy mezi plazenim a stojenim
		self.cooldown = 0	#Cooldown mezi zmenenim stavu (stani/plazeni)
		self.GroundSpeed = 235	#rychlost pohybu normalne


	def update(self, time_passed):
		pressed = pygame.key.get_pressed()
		if event.type == pygame.KEYDOWN: #toto handeluje plazeni / chozeni
			if event.key == pygame.K_RCTRL:
				if self.cooldown <= 0:
					if self.Zet == 1: #TOTO JE PLAZENI
						self.CharacterSirka, self.CharacterVyska= 150, 50
						self.GroundSpeed = 50
						self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
						self.image.fill((255, 0, 0))
						self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))
						self.Zet *= -1
					elif self.Zet == -1: #TOHLE JE KDYZ HRAC STOJI
						#Check, jestli je nad tebou nejaky blok, ktery by mohl branit zvednuti se
						self.CharacterSirka, self.CharacterVyska= 50, 150
						self.GroundSpeed = 235
						self.image = pygame.Surface((self.CharacterSirka, self.CharacterVyska))
						self.image.fill((255, 0, 0))
						self.rect = self.image.get_rect(midbottom=(round(self.pos.x), round(self.pos.y)))
						self.Zet *= -1
					self.cooldown = 2

		if self.cooldown > 0:
			self.cooldown -= time_passed

		if pressed[pygame.K_LEFT] or pressed[pygame.K_a]: #pohyb doleva
			self.move.x -= self.GroundSpeed
		if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:#pohyb doleva
				self.move.x += self.GroundSpeed	

		if pressed[pygame.K_UP] or pressed[pygame.K_w]: #Skakani
			if self.OnGround:
				if self.Zet == 1:
					self.move.y = -1150
				else:
					self.move.y = -300
			jumping = True
		else:
			jumping = False

		if pressed[pygame.K_DOWN] or pressed[pygame.K_s]: #pohyb dolu (asi pak po zdech)
			if not self.OnGround:
				self.move.y += self.GroundSpeed

		if pressed[pygame.K_RCTRL]:
			CharacterVyska = 50

		self.pos = self.pos + self.move * time_passed	#kalkulace pohybu
		self.move.x *= 0.8	#Treni
		self.move.y += 5000 * time_passed	#Gravitace

		self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))
		if self.rect.left < 0:	#kontrola kolize se zdi nalevo
			self.rect.left = 0
			self.pos.x = self.rect.centerx
		if self.rect.right > 1280:	#kontrola kolize se zdi napravo
			self.rect.right = 1280
			self.pos.x = self.rect.centerx

		if self.rect.bottom >= 720:	#kolize s podlahou
			self.rect.bottom = 720
			self.move.y = 0  # Tohle resetne pohyb smerem dolu
			self.OnGround = True
		else:
			self.OnGround = False

		return pressed



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
print(AllCaveSprites)

OnTopBlock = True #jak vim ze je postava na hore na bloku a nemam aplikovat teleport do strany
jumping = False

class Enemy(pygame.sprite.Sprite): #toto bude nepritel
	def __init__(self, x, y, OnGround):
		super().__init__()
		self.pos = pygame.math.Vector2(x, y)
		self.move = pygame.math.Vector2()
		self.OnGround = OnGround
		self.image = pygame.Surface((80, 200))
		self.image.fill((200, 0, 200)) 
		self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))
		self.GroundSpeed = 235	#Rychlost pohybu

	def patrol(self):
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_HOME]:
			self.move.x -= self.GroundSpeed

		self.pos = self.pos + self.move * time_passed	#kalkulace pohybu
		self.move.x *= 0.8	#Treni
		self.move.y += 5000 * time_passed	#Gravitace
		self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))
		if self.rect.left < 0:	#kontrola kolize se zdi nalevo
			self.rect.left = 0
			self.pos.x = self.rect.centerx
		if self.rect.right > 1280:	#kontrola kolize se zdi napravo
			self.rect.right = 1280
			self.pos.x = self.rect.centerx

		if self.rect.bottom >= 720:	#kolize s podlahou
			self.rect.bottom = 720
			self.move.y = 0  # Tohle resetne pohyb smerem dolu

	#def hunt(self):
        #showdown
		#print("1889")

	def killCheck(self):
		kolizeCheck = pygame.sprite.spritecollide(Hrac, EnemySprite, False)
		if kolizeCheck:
			print('ted ma hrac umrit')



Nepritel = (Enemy(1000, 700, True))
EnemySprite = pygame.sprite.GroupSingle()
EnemySprite.add(Nepritel)

KolizovanyBloky = []

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	screen.fill((0,0,0))
	time_passed = clock.tick(60) / 1000.0

	#KOLIZE SE ZDMI
	Hrac.rect.centerx = round(Hrac.pos.x)
	Hrac.rect.centery = round(Hrac.pos.y)
	Obdelniky = [block.rect for block in Bloky]

	IndexKolizi = Hrac.rect.collidelist(Obdelniky)

	if IndexKolizi >= 0:  #Pokud nastane kolize
		if IndexKolizi not in KolizovanyBloky:  #CHeck jestli už není v listu kolizovanejch bloku
			KolizovanyBloky.append(IndexKolizi)
			print(f"do tohoto bloku narazil: {IndexKolizi}")
		print(f"Techto se dotyka: {KolizovanyBloky}")
		for index, sprite in enumerate(AllCaveSprites):
#			print(f"Index: {index}")
			if index == IndexKolizi:
				if not OnTopBlock and not jumping: #pokud hrac neni na vrchu bloku
					if Hrac.move.x > 0: #KOLIZE V LEVO
						if Hrac.rect.right > sprite.rect.left and not jumping:
							sprite.Lef_col = True
							Hrac.rect.right = sprite.rect.left
							Hrac.move.x = 0  
							Hrac.pos.x = Hrac.rect.centerx #sjednoceni logicke a graficke casti hrace
						else:
							sprite.Lef_col = False
					elif Hrac.move.x < 0: 		#KOLIZE V PRAVO
						if Hrac.rect.left < sprite.rect.right and not jumping:
							sprite.Rig_col = True
							Hrac.rect.left = sprite.rect.right
							Hrac.move.x = 0
							Hrac.pos.x = Hrac.rect.centerx
						else: 
							sprite.Rig_col = False

				if Hrac.move.y > 0: #KOLIZE DOLE
					if Hrac.rect.bottom > sprite.rect.top:
						sprite.Bot_col = True
						Hrac.rect.bottom = sprite.rect.top
						Hrac.move.y = 0
						Hrac.pos.y = Hrac.rect.bottom +1
						Hrac.OnGround = True
						OnTopBlock = True
					else:
						sprite.Bot_col = False

				elif Hrac.move.y < 0: #KOLIZE NAHORE
					if Hrac.rect.top > sprite.rect.bottom:
						sprite.Top_col = True
						Hrac.rect.top = sprite.rect.bottom
						Hrac.move.y *= -1
						Hrac.pos.y = Hrac.rect.bottom
					else:
						sprite.Top_col = False
				else:
					OnTopBlock = False
		KolizovanyBloky.clear()	#clearuje list bloku, do kterych jses narazenej

	Nepritel.patrol()
	Nepritel.killCheck()
#	Nepritel.hunt()
	EnemySprite.draw(screen)

	HracSprite.update(time_passed)


	HracSprite.draw(screen)
	AllCaveSprites.draw(screen)


	pygame.display.flip()
	clock.tick(60)

pygame.quit()