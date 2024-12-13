import pygame
import sys

def difficulty_menu():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Main Menu")

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)

    # Create difficulty rects
    difficulty_rects = [
        (pygame.Rect(340, 400, 150, 150), green, 1),    # Easy
        (pygame.Rect(540, 400, 150, 150), yellow, 2),  # Medium 
        (pygame.Rect(740, 400, 150, 150), red, 3)    # Hard
    ]

    # Font setup
    font = pygame.font.Font(None, 70)
    title = font.render("Choose Your Difficulty:", True, white)
    title_rect = title.get_rect(center=(640, 200))

    # Main menu loop
    selected_difficulty = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, color, difficulty in difficulty_rects:
                    if rect.collidepoint(event.pos):
                        selected_difficulty = difficulty
                        running = False

        # Drawing
        screen.fill(black)
        screen.blit(title, title_rect)
        
        # Draw buttons
        for rect, color, _ in difficulty_rects:
            pygame.draw.rect(screen, color, rect)

        pygame.display.flip()

    pygame.quit()
    return selected_difficulty