import moderngl
import numpy as np
import pygame
import pygame.math as pgmath

class GPULightingSystem:
    def __init__(self, screen_width, screen_height):
        # Initialize OpenGL context
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create OpenGL context
        pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)
        
        # Create ModernGL context
        self.ctx = moderngl.create_context()
        
        # Shader for light rendering
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec2 u_light_pos;
                uniform float u_light_radius;
                uniform vec2 u_screen_size;
                uniform sampler2D u_occlusion_map;
                
                out vec4 f_color;
                
                void main() {
                    // Normalize screen coordinates
                    vec2 screen_pos = gl_FragCoord.xy / u_screen_size;
                    
                    // Calculate distance to light source
                    vec2 light_screen_pos = u_light_pos / u_screen_size;
                    float distance = length(screen_pos - light_screen_pos);
                    
                    // Check occlusion
                    float occlusion = texture(u_occlusion_map, screen_pos).r;
                    
                    // Soft light falloff
                    float intensity = 1.0 - smoothstep(0.0, u_light_radius / u_screen_size.x, distance);
                    intensity *= (1.0 - occlusion);
                    
                    f_color = vec4(1.0, 0.8, 0.6, intensity * 0.8);
                }
            '''
        )
        
        # Create screen-sized quad
        vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0,  1.0,
            1.0,  1.0
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '2f', 'in_position')])
        
        # Occlusion texture
        self.occlusion_texture = self.ctx.texture((screen_width, screen_height), 1)
        
    def create_occlusion_map(self, wall_sprites, camera_offset):
        # Create numpy array for occlusion
        occlusion = np.zeros((self.screen_height, self.screen_width), dtype=np.float32)
        
        # Mark wall positions
        for wall in wall_sprites:
            # Calculate screen position
            x = int(wall.rect.x - camera_offset[0])
            y = int(wall.rect.y - camera_offset[1])
            w = wall.rect.width
            h = wall.rect.height
            
            # Ensure within screen bounds
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            w = min(w, self.screen_width - x)
            h = min(h, self.screen_height - y)
            
            # Mark as occluded
            occlusion[y:y+h, x:x+w] = 1.0
        
        # Upload to GPU
        self.occlusion_texture.write(occlusion.tobytes())
        
    def render_light(self, screen, player, camera_offset):
        # Clear the screen
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Set uniforms
        self.prog['u_light_pos'].value = (
            player.rect.centerx - camera_offset[0], 
            self.screen_height - (player.rect.centery - camera_offset[1])
        )
        self.prog['u_light_radius'].value = 300.0  # Configurable light radius
        self.prog['u_screen_size'].value = (self.screen_width, self.screen_height)
        
        # Bind occlusion texture
        self.occlusion_texture.use()
        
        # Render light
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        # Blit to pygame surface
        light_surface = pygame.image.fromstring(
            self.ctx.screen.read(), 
            (self.screen_width, self.screen_height), 
            'RGBA'
        )
        
        # Blend light with screen
        screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

# In your game loop
def render_game(game_state):
    # Existing rendering code...
    
    # Create occlusion map
    game_state.LightingSystem.create_occlusion_map(
        game_state.CaveRockSprites, 
        (game_state.camera.offset.x, game_state.camera.offset.y)
    )
    
    # Render light
    game_state.LightingSystem.render_light(
        game_state.screen, 
        game_state.player, 
        (game_state.camera.offset.x, game_state.camera.offset.y)
    )