import math
import pygame
import cas
#import threading
ds = (50,50)
res = (720,900)
const = min(res[0]/ds[0],res[1]/ds[1])
mapg = cas.MapGrid(ds)
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
			raise OverflowError
		if i == r-1 and not hd :
			raise OverflowError
	return rax
class kapka :
	def __init__(self, pos) -> None:
		self.x = pos[0]
		self.y = pos[1] # Změna!! y=0 je nyní dolní okraj obrazovky 
		self.pref = pygame.Vector2(0,-1)
	def mpos(self) :
		self.pref += pygame.Vector2(0,-0.7)
		m = 0
		for i in vecs :
			if vhard(self.x,self.y,self.pref.rotate(m)) > vhard(self.x,self.y,self.pref.rotate(i)) : #5 def r
				m = i
		self.pref= self.pref.normalize().rotate(m)
		m=vhard(self.x,self.y,self.pref, hd=False, bid=2)
		self.x = m[0]
		self.y = m[1]
def savemap(map) :
	fmap = open("map", "w")
	for x in map :
		buffer = ""
		for y in x :
			buffer+=str(y) # kašleme na +',' 
		fmap.write(buffer+"\n")
pygame.init()
kapky = []
screen = pygame.display.set_mode(res)
running = True
font = pygame.font.SysFont("", 25)
while running :
	screen.fill((0,0,0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	for i,x in enumerate(mapg.map) :
		for j,y in enumerate(x) :
			pygame.draw.rect(screen, hcol[y], (i*const+(res[0]-ds[0]*const)/2,res[1]-j*const-(res[1]-ds[1]*const)/2,math.ceil(const),math.ceil(const)))
	for x in kapky :
		if x.x > ds[0] or x.x < 0 or x.y > ds[1] or x.y < 0:
			kapky.remove(x)
			del x
			continue
		try :
			x.mpos()
		except OverflowError :
			kapky.remove(x)
			del x
			continue
	if pygame.mouse.get_pressed()[0] :
		kapky.append(kapka((int((pygame.mouse.get_pos()[0]-(res[0]-ds[0]*const)/2)/const),int((res[1]-pygame.mouse.get_pos()[1]-(res[1]-ds[1]*const)/2)/const))))
	if pygame.mouse.get_pressed()[1] :
		kapky = []
	screen.blit(font.render(str(len(kapky)), False,(255, 0,0)), pygame.mouse.get_pos()) 
	#str(int((pygame.mouse.get_pos()[0]-(res[0]-ds[0]*const)/2)/const)) + "  " + str(int((res[1]-pygame.mouse.get_pos()[1]-(res[1]-ds[1]*const)/2)/const)) ##Coords na debug
	pygame.display.flip()	
if input("Save? Y/N").upper() == 'Y' :
	savemap(mapg.map)
pygame.quit()
