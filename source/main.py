import pygame
from game_engine import main, COLORS


pygame.display.set_caption('NuttyPutty')
icon = pygame.image.load("..\Textury\Ikona2.png")
pygame.display.set_icon(icon)


main()