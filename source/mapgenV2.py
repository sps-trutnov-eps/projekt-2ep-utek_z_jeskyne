import pygame
import cas
import threading

mapg = cas.MapGrid(200,100)
mapg._generate_outside_terrain(mapg.outside_terrain_grid, 3) # zatím jen 0 a 1, mají přidružené k tomu ještě tvrdost kvůli budoucím materiálům

vecs = [-80, -40, 0, 40, 80]
hval = (1, 0.3) #hodnoty tvrdosti

def vhard(x,y,vec, r = 7) : #Pamatovat že je to programovaný v [sloupec][index] systému, to jest x, y
	if vec.x <=0 :
		a=-1
	else :
		a=1
	if vec.y <=0 :
		b=-1
	else :
		b=1
	p_angle = vec.angle_to(pygame.Vector2(0,1))%90

	rax = 0
	res = 0
	bres = 0
	up = 0
	for i in r :
		up = (1 if 90/2^i < p_angle else 0)
		res = bres + up
		bres = res
		if up : #hihi hehe pokud int
			p_angle-= 90/2^i
		rax+=hval[mapg.outside_terrain_grid[x+(i-res)*a][y+res*b]]
	return rax
class kapka :
	def __init__(self, pos, scale) -> None:
		self.x = pos[0]
		self.y = pos[1] # Změna!! y=0 je nyní dolní okraj obrazovky 
		self.scale = scale
		self.pref = pygame.Vector2(0,-1)
	def mpos(self) :
		#
		
		
running = True
while running :
	pass
