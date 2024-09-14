import random
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
##

p_fork = 0.09
p_tweak = 0.23
p_edge = 0.9
p_end = 0.1
r = 250
drops = []
chaos = set()

class node : #Jednotky, které když se spojí tak tvoří náš jeskyňoví systém
    def __init__(self, x, y, parent, scale) -> None:
        self.x = x
        self.y = y
        self.parents = [parent]
        self.children = []
        self.scale = 1
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
    def __init__(self,x,y,vect=pygame.Vector2(),scale=3) -> None:
        self.x =x
        self.y =y
        self.vect = vect
        self.cur : node = None
        self.scale = scale
    def trace(self) : #Zaznamenat jednotku za kapkou.
        self.cur.children.append(node(self.x,self.y,self.cur))
        self.cur = self.cur.children[0]
        chaos.add(self.cur)
    def move_dir(self, im = False) : #Krok pro kapku. Různé změny sestupu kapky se zde aplikují podle šance
        self.vect.move_towards_ip((0,-1),0.1) #Gravitace
        #Šance
        if random.random()<=p_fork * (self.scale/5+0.4) :
            drops.append(drop(self.x,self.y,self.vect.reflect((0,1))))
            drops[-1].move_dir(True)
        if random.random()<=p_end : #TODO scale modifikuje šanci
            drops.remove(self)
            del self
            return
        if random.random()<=p_edge :
            self.vect.move_towards_ip(random.choice(((1,0),(-1,0),(0,0),(0,0.5))), 0.7)
        if random.random()<=p_tweak :
            self.vect.move_towards_ip(random.choice(((1,0),(-1,0),(0,0))), 0.2)
        self.vect.normalize_ip()
        #TODO actual hybani atd
        self.scale -=0.2
        if not im : #Po rozdvojení kapek, aby kapka ihned nesklouzla zpět a vyvolala rec_scale, dostane jedno kolo s imunitou vůči tomu. TODO: co ta orig kapka
            for x in chaos :
                if abs(x.x-self.x) <= r and abs(x.y-self.y) <= r : # Jsou blízko? TODO: Započítat velikost dané jeskyně a kapky samotné.
                    rec_scale()
                    drops.remove(self)
                    del self
                    return
pygame.time.set_timer(10, 300)
while running:
    for event in pygame.event.get():
        #if event.type == 10 :
            #(-1)*random.randint(0,1)
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0,0,0))


    pygame.display.flip()

    clock.tick(20)

pygame.quit()