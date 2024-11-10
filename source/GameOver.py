import pygame
import sys

def game_over_screen():
    # Initialize pygame
    pygame.init()
    
    # Set up screen
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Game Over Screen")
    
    # Define colors and font
    black = (0, 0, 0)
    white = (255, 255, 255)
    font = pygame.font.Font(None, 100)
    
    # Render text
    text1 = font.render("Game Over! You lost!", True, white)
    text_rect = text1.get_rect(center=(640, 360))
    # Render text
    text2 = font.render("Game Over! You won!", True, white)
    text_rect = text2.get_rect(center=(640, 360))
    
    # Main display loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Fill the screen with black
        screen.fill(black)
        
        # Draw the text
        screen.blit(text1, text_rect)
        #screen.blit(text2, text_rect)
        
        # Update the display
        pygame.display.flip()
