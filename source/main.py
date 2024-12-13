import pygame, os
from game_engine import main, COLORS
from Menu import difficulty_menu

file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(file_dir, os.path.pardir))
Ikona = os.path.join(parent_dir, "Textury", "Ikona01.png")
map_file = os.path.join(parent_dir, "map")
game_file = os.path.join(file_dir, "game_engine.py")
difficulty_file = os.path.join(file_dir, "diff")
mgc = os.path.join(file_dir, "mgc.py")

difficulty = difficulty_menu()

# Save the difficulty to a file
with open(difficulty_file, "w") as file:
    file.write(str(difficulty))

pygame.display.set_caption('Dangerous Caves')
icon = pygame.image.load(Ikona)
pygame.display.set_icon(icon)

#os.system(str("python ")+mgc + str() + str() )
    
#genrujeme mapu os system
os.system(f"python {game_file}")

#quit
