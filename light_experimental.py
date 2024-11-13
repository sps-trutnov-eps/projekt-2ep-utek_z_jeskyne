import pygame
import math
from typing import List, Tuple

class LightingSystem:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.light_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.ray_count = 360  # Reduced number of rays
        self.max_light_distance = 200
        
    def calculate_intersection(self, start: Tuple[float, float], angle: float, 
                             wall: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple[float, float]:
        x1, y1 = start
        x2 = x1 + math.cos(angle) * self.max_light_distance
        y2 = y1 + math.sin(angle) * self.max_light_distance
        
        x3, y3 = wall[0]
        x4, y4 = wall[1]
        
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return None
            
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            return (px, py)
        return None

    def get_wall_segments(self, tile_map: List[List[int]], tile_size: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
            walls = []
            for y, row in enumerate(tile_map):
                for x, tile in enumerate(row):
                    if tile == 1:  # Assuming 1 represents a wall
                        # Create wall segments for each edge of the tile
                        x1, y1 = x * tile_size, y * tile_size
                        x2, y2 = x1 + tile_size, y1 + tile_size
                    
                        # Add all four sides of the tile
                        walls.append(((x1, y1), (x2, y1)))  # Top
                        walls.append(((x2, y1), (x2, y2)))  # Right
                        walls.append(((x2, y2), (x1, y2)))  # Bottom
                        walls.append(((x1, y2), (x1, y1)))  # Left
            return walls

    def cast_light(self, light_pos: Tuple[float, float], walls: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:
        self.light_surface.fill((0, 0, 0, 255))
        
        light_vertices = []
        
        # Cast rays with slightly offset angles for each main ray
        for i in range(self.ray_count):
            angle = (i / self.ray_count) * math.pi * 2
            
            # Cast three rays for each angle: main ray and two slightly offset rays
            angles = [
                angle - 0.01,  # Slightly before
                angle,         # Main ray
                angle + 0.01   # Slightly after
            ]
            
            for ray_angle in angles:
                closest_point = None
                closest_dist = self.max_light_distance
                
                for wall in walls:
                    intersection = self.calculate_intersection(light_pos, ray_angle, wall)
                    if intersection:
                        dist = math.sqrt((light_pos[0] - intersection[0])**2 + 
                                       (light_pos[1] - intersection[1])**2)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_point = intersection
                
                if not closest_point:
                    closest_point = (light_pos[0] + math.cos(ray_angle) * self.max_light_distance,
                                   light_pos[1] + math.sin(ray_angle) * self.max_light_distance)
                
                light_vertices.append(closest_point)
        
        # Sort vertices by angle to ensure proper polygon drawing
        center_x, center_y = light_pos
        sorted_vertices = sorted(light_vertices, 
                               key=lambda point: math.atan2(point[1] - center_y, 
                                                          point[0] - center_x))
        
        if sorted_vertices:
            # Draw the light polygon
            vertices = [(int(x), int(y)) for x in [center_x] for y in [center_y]] + \
                      [(int(x), int(y)) for x, y in sorted_vertices]
            
            light_cone = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            pygame.draw.polygon(light_cone, (255, 255, 200, 50), vertices)
            self.light_surface.blit(light_cone, (0, 0))

    def apply_lighting(self, screen: pygame.Surface) -> None:
        screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

# The rest of the code remains the same...

# Example usage:
def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    
    # Initialize lighting system
    lighting = LightingSystem(screen_width, screen_height)
    
    # Example tile map (0 = empty, 1 = wall)
    tile_map = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    tile_size = 50
    walls = lighting.get_wall_segments(tile_map, tile_size)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        

        fps = int(clock.get_fps())
        pygame.display.set_caption(f"My Game - FPS: {fps}")
        # Get mouse position for light source
        light_pos = pygame.mouse.get_pos()
        
        # Draw background and walls
        screen.fill((50, 50, 50))
        for y, row in enumerate(tile_map):
            for x, tile in enumerate(row):
                if tile == 1:
                    pygame.draw.rect(screen, (100, 100, 100),
                                   (x * tile_size, y * tile_size, tile_size, tile_size))
        
        # Update and apply lighting
        lighting.cast_light(light_pos, walls)
        lighting.apply_lighting(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()