import pygame, os
from game_engine import main, COLORS

file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(file_dir, os.path.pardir))
Ikona = os.path.join(parent_dir, "Textury", "Ikona01.png")

pygame.display.set_caption('NuttyPutty')
icon = pygame.image.load(Ikona)
pygame.display.set_icon(icon)


main()