from copy import deepcopy
import random
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
##

p_fork = 0.12
p_tweak = 0.23
p_edge = 0.4
p_end = 0.035
r = 250
drops = []
chaos = set()

class node : #Jednotky, které když se spojí tak tvoří náš jeskyňoví systém
	def __init__(self, x, y, parent, scale) -> None:
		self.x = x
		self.y = y
		self.parents = [parent,]
		self.children = []
		self.scale = scale
	def append(self, a) : #Přidání nového děcka
		self.children.append(a)
	def foster(self, a) :
		self.parents.append(a)
	def sup(self, a) : #Zvětšení jeskyně. Používá rec_scale
		self.scale += a / (self.scale/3)
def rec_scale(a : node) : #Rekurzivní funkce na zvětšení jeskyní na které kapka narazí. Po spuštění se kapka maže.
	a.sup(1 + random.random())
	for x in a.children :
		rec_scale(x)
class drop : #Kapka. Zanechává za sebou jednotky. Rádoby erozní typ mapgenu.
	def __init__(self,x,y,scale,vect=pygame.Vector2(0,1)) -> None:
		self.x =x
		self.y =y
		self.vect : pygame.Vector2 = vect
		self.cur : node = node(x,y,None,scale)
		chaos.add(self.cur)
		self.scale = scale
	def trace(self) : #Zaznamenat jednotku za kapkou.
		self.cur.children.append(node(self.x,self.y,self.cur,self.scale))
		self.cur = self.cur.children[0]
		chaos.add(deepcopy(self.cur))
	def move_dir(self, im = False) : #Krok pro kapku. Různé změny sestupu kapky se zde aplikují podle šance
		self.vect.move_towards_ip((0,1),0.15) #Gravitace
		#Šance
		if random.random()<=p_fork * (self.scale/5+0.4) :
			drops.append(drop(self.x,self.y,random.random()*self.scale,self.vect.reflect((0,1))))
			self.scale -= drops[-1].scale
			drops[-1].move_dir(True)
		if random.random()<=p_end / ((2*self.scale+0.5)/4) : 
			drops.remove(self)
			del self
			return
		if random.random()<=p_edge :
			self.vect.move_towards_ip(random.choice(((1,0),(-1,0),(0,1),(0,-0.4))), 0.7)
		if random.random()<=p_tweak :
			self.vect.move_towards_ip(random.choice(((1,0),(-1,0),(0,1))), 0.2)
		norm = self.vect.normalize()
		self.x += norm.x * r * (1.3 if im else 1)
		self.y += norm.y * r * (1.3 if im else 1)
		self.scale = self.cur.scale #V případě že byla tato jeskyně posílena voláním rec_scale
		self.scale -=0.1
		if not im : #Po rozdvojení kapek, aby kapka ihned nesklouzla zpět a vyvolala rec_scale, dostane jedno kolo s imunitou vůči tomu. TODO: co ta orig kapka
			for x in chaos :
				if abs(x.x-self.x) <= r*0.8 and abs(x.y-self.y) <= r*0.8 and x != self.cur : #TODO započítat velikost #*(x.scale/3)*(self.scale/3)
					rec_scale(self.cur)
					drops.remove(self)
					del self
					return
		self.trace() #zaznamenat posun s node
pygame.time.set_timer(10, 300)
drops.append(drop(0,1500,6))
drops.append(drop(500,1500,6))
drops.append(drop(-900,1500,6))
drops.append(drop(-400,1900,6))
while running:
	for event in pygame.event.get():
		if event.type == 10 :
			for x in drops :
				x.move_dir()
			print(len(chaos))
		if event.type == pygame.QUIT:
			running = False
	
	screen.fill((0,0,0))
	for x in drops :
		pygame.draw.circle(screen, (255,0,0),(x.x/15+640,x.y/15),5,2)
	for x in chaos :
		pygame.draw.circle(screen, (255,255,255),(x.x/15+640,x.y/15),4)
	if len(drops) <1 :
		running=False
	pygame.display.flip()

	clock.tick(20)

pygame.quit()