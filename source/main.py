import pygame, os
import pygame_light2d as pl2d
from pygame_light2d import LightingEngine, PointLight, Hull
from game_engine import main, COLORS
from Menu import difficulty_menu

file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(file_dir, os.path.pardir))
Ikona = os.path.join(parent_dir, "Textury", "Ikona01.png")
map_file = os.path.join(parent_dir, "map")
game_file = os.path.join(parent_dir, "game_engine.py")


pygame.display.set_caption('NuttyPutty')
icon = pygame.image.load(Ikona)
pygame.display.set_icon(icon)

difficulty = difficulty_menu()
#genrujeme mapu os system 
# gufbirebkg d game engine
#quit
