import math
import pygame
import cas
import threading

mapg = cas.MapGrid(200,100)
mapg._generate_outside_terrain(mapg.map, 3) # zatím jen 0 a 1, mají přidružené k tomu ještě tvrdost kvůli budoucím materiálům

vecs = [-80, -40, 0, 40, 80]
hval = (1, 0.3) #hodnoty tvrdosti

def vhard(x,y,vec, r = 5, hd=True, bid = -1) : #Pamatovat že je to programovaný v [sloupec][index] systému, to jest x, y
	p_angle = vec.angle_to(pygame.Vector2(0,1))%90

	if hd : 
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
		if hd :
			rax+=hval[mapg.map[x+math.copysign((i-res), vec.x)][y+math.copysign(res, vec.y)]]
		if bid != -1 :
			hval[mapg.map[x+math.copysign((i-res), vec.x)][y+math.copysign(res, vec.y)]] = bid
		elif i == r :
			return (x+math.copysign((i-res), vec.x),y+math.copysign(res, vec.y))
	return rax
class kapka :
	def __init__(self, pos, scale) -> None:
		self.x = pos[0]
		self.y = pos[1] # Změna!! y=0 je nyní dolní okraj obrazovky 
		self.scale = scale
		self.pref = pygame.Vector2(0,-1)
	def mpos(self) :
		self.pref += pygame.Vector2(0,-0.1)
		m = 0
		for i in vecs :
			if vhard(self.x,self.y,self.pref.rotate(m)) > vhard(self.x,self.y,self.pref.rotate(i)) :
				m = i
		self.pref.rotate_ip(i)
		vhard(self.x,self.y,self.pref, hd=False, bid=2)
		
		
		
running = True
while running :
	pass
