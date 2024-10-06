import pygame
from pygame import key


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
OnGround = True
AirSpeed = 260		#rychlost pohybu mid air
GroundSpeed = 235	#rychlost pohybu normalne

class character(pygame.sprite.Sprite):
	def __init__(self, x, y, HP, OnGround):
		super().__init__()
		self.pos = pygame.math.Vector2(x, y)
		self.move = pygame.math.Vector2()
		self.HP = HP
		self.OnGround = OnGround
#		self.image = pygame.image.load('character.png').convert_alpha()
		self.image = pygame.Surface((50, 150))
		self.image.fill((255, 0, 0)) 
		self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))


	def update(self, time_passed):
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:# pohyb doleva a ruzne rychlosti ve vzduchu a na zemi
			if not self.OnGround:
				self.move.x -= AirSpeed
			else:
				self.move.x -= GroundSpeed
		if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:# pohyb doprava a ruzne rychlosti ve vzduchu a na zemi
			if not self.OnGround:
				self.move.x += AirSpeed
			else:
				self.move.x += GroundSpeed	

		if pressed[pygame.K_UP] or pressed[pygame.K_w]: #Skakani
			if self.OnGround:
				self.move.y = -1150
			jumping = True
		else:
			jumping = False

		if pressed[pygame.K_DOWN] or pressed[pygame.K_s]: #pohyb dolu (asi pak po zdech)
			if not self.OnGround:
				self.move.y += GroundSpeed

		self.pos = self.pos + self.move * time_passed	#kalkulace pohybu pana Kalkulatora
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



Hrac = character(100, 720, 100, OnGround)

allSprites = pygame.sprite.GroupSingle()
allSprites.add(Hrac)

class environmentblock(pygame.sprite.Sprite):
	def __init__(self, x, y, sirka, vyska):
		super().__init__()
		self.pos = pygame.math.Vector2(x, y)
		self.move = pygame.math.Vector2()
		self.sirka = sirka
		self.vyska = vyska
		self.image = pygame.Surface((200, 20))
		self.image.fill((255, 255, 255)) 
		self.rect = self.image.get_rect(midbottom = (round(self.pos.x), round(self.pos.y)))


AllCaveSprites = pygame.sprite.Group()
Bloky = (environmentblock(300, 680, 200, 50),environmentblock(700, 450, 600, 50),environmentblock(600, 610, 10, 70))
AllCaveSprites.add(Bloky)

OnTopBlock = True #jak vim ze je postava na hore na bloku a nemam aplikovat teleport do strany
jumping = False 
#TODO: kdyz jses ve skoku a zaroven jdes do strany, aby te to neteleportovalo na kraj bloku

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	screen.fill((0,0,0))
	time_passed = clock.tick(60) / 1000.0

	KolizovanySprite = pygame.sprite.spritecollide(Hrac, AllCaveSprites, False)
	
	
	#KOLIZE SE ZDMI
	Hrac.rect.centerx = round(Hrac.pos.x)
	Hrac.rect.centery = round(Hrac.pos.y)
	for sprite in KolizovanySprite:
		if not OnTopBlock and not jumping: #pokud hrac neni na vrchu bloku
			if Hrac.move.x > 0:
				if Hrac.rect.right > sprite.rect.left:
					Hrac.rect.right = sprite.rect.left  
					Hrac.move.x = 0  
					Hrac.pos.x = Hrac.rect.centerx #sjednoceni logicke a graficke casti hrace
					print('kolize v levo')
			if Hrac.move.x < 0:
				if Hrac.rect.left < sprite.rect.right:
					Hrac.rect.left = sprite.rect.right
					Hrac.move.x = 0
					Hrac.pos.x = Hrac.rect.centerx
					print('kolize v pravo')

		if Hrac.move.y > 0: #pohyb dolu
			if Hrac.rect.bottom > sprite.rect.top:
				Hrac.rect.bottom = sprite.rect.top
				Hrac.move.y = 0
				Hrac.pos.y = Hrac.rect.bottom +1
				Hrac.OnGround = True
				OnTopBlock = True
				print('kolize dole')
		elif Hrac.move.y < 0: #pohyb nahoru
			if Hrac.rect.top > sprite.rect.bottom:
				Hrac.rect.top = sprite.rect.bottom
				Hrac.move.y *= -1
				Hrac.pos.y = Hrac.rect.bottom
				print('kolize nahore')
		else:
			OnTopBlock = False



#	Hrac.pos.x = Hrac.rect.centerx
#	Hrac.pos.y = Hrac.rect.bottom


	allSprites.update(time_passed)

	allSprites.draw(screen)
	AllCaveSprites.draw(screen)


	pygame.display.flip()
	clock.tick(60)

pygame.quit()