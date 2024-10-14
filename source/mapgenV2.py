import math
import pygame
import cas
#import threading

mapg = cas.MapGrid(200,100)
mapg.map = mapg._generate_outside_terrain(mapg.map, 4) # zatím jen 0 a 1, mají přidružené k tomu ještě tvrdost kvůli budoucím materiálům

vecs = (-80, -40, 0, 40, 80)
hval = (1, 0.3, 0) #hodnoty tvrdosti
hcol = ((150,150,150), (75,75,75), (0,0,0))
def vhard(x,y,vec, r = 5, hd=True, bid = -1) : #Pamatovat že je to programovaný v [sloupec][index] systému, to jest x, y
	p_angle = vec.angle_to(pygame.Vector2(0,1))%90

	if hd : 
		rax = 0
	res = 0
	bres = 0
	up = 0
	for i in range(r) :
		up = (1 if 90/2**i < p_angle else 0)
		res = bres + up
		bres = res
		if up : #hihi hehe pokud int
			p_angle-= 90/2**i
		try :
			if bid != -1 :
				mapg.setblock((x+int(math.copysign((i-res), vec.x)),y+int(math.copysign(res, vec.y))),bid)
			if hd :
				rax+=hval[mapg.map[x+int(math.copysign((i-res), vec.x))][y+int(math.copysign(res, vec.y))]]
			elif i == r-1 :
				return (x+int(math.copysign((i-res), vec.x)),y+int(math.copysign(res, vec.y)))
		except IndexError :
			continue
		except IndexError and i == r-1 and not hd :
			raise OverflowError
	return rax
class kapka :
	def __init__(self, pos, scale) -> None:
		self.x = pos[0]
		self.y = pos[1] # Změna!! y=0 je nyní dolní okraj obrazovky 
		#self.scale = scale
		self.pref = pygame.Vector2(0,-1)
	def mpos(self) :
		self.pref += pygame.Vector2(0,-0.1)
		#self.scale *= 1.5
		m = 0
		for i in vecs :
			if vhard(self.x,self.y,self.pref.rotate(m)) > vhard(self.x,self.y,self.pref.rotate(i)) : #5 def r
				m = i
		self.pref.rotate_ip(m)
		#self.scale -= self.scale*m/
		m=vhard(self.x,self.y,self.pref, hd=False, bid=2)
		self.x = m[0]
		self.y = m[1]
pygame.init()
kapky = []
screen = pygame.display.set_mode((1280, 720))
running = True
font = pygame.font.SysFont("", 25)
while running :
	screen.fill((0,0,0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	for i,x in enumerate(mapg.map) :
		for j,y in enumerate(x) :
			pygame.draw.rect(screen, hcol[y], (math.floor(6.4*i),math.floor(680-6.4*j),7,7))
	for x in kapky :
		if x.x > 199 or x.x < 0 or x.y > 99 or x.y < 0:
			kapky.remove(x)
			del x
			continue
		try :
			x.mpos()
		except OverflowError :
			kapky.remove(x)
			del x
			continue
	if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[1]>40 and pygame.mouse.get_pos()[1]<680 :
		kapky.append(kapka((math.floor(pygame.mouse.get_pos()[0]/6.4),100-math.floor((pygame.mouse.get_pos()[1]-40)/6.4)), 5))
	if pygame.mouse.get_pressed()[1] :
		kapky = []
	screen.blit(font.render(str(math.floor(pygame.mouse.get_pos()[0]/6.4)) + "  " + str(100-math.floor((pygame.mouse.get_pos()[1]-40)/6.4)), False,(255, 0,0)), pygame.mouse.get_pos())
	pygame.display.flip()	
pygame.quit()