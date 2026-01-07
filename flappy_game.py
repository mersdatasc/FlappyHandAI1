import pygame
import random
import numpy as np 

SKY_BLUE = (135, 206, 235)
BIRD_YELLOW = (255, 220, 0)
PIPE_GREEN = (34, 177, 76)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

class Bird:
    def __init__(self):
        self.x, self.y = 80, 300
        self.radius = 18
        self.velocity = 0
        self.gravity = 0.45
        self.lift = -7.5

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y > 600 - self.radius: self.y = 600 - self.radius
        if self.y < self.radius: self.y = self.radius

    def jump(self):
        self.velocity = self.lift

    def draw(self, screen):
        pygame.draw.circle(screen, BIRD_YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        pygame.draw.circle(screen, WHITE, (int(self.x + 8), int(self.y - 5)), 6)
        pygame.draw.circle(screen, BLACK, (int(self.x + 10), int(self.y - 5)), 2)
        pygame.draw.polygon(screen, (255, 69, 0), [(self.x+12, self.y), (self.x+22, self.y+4), (self.x+12, self.y+8)])

class Pipe:
    def __init__(self):
        self.x, self.width, self.gap = 400, 65, 170
        self.top = random.randint(100, 330)
        self.speed = 3.5
        self.passed = False

    def update(self): self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_GREEN, (self.x, 0, self.width, self.top))
        pygame.draw.rect(screen, BLACK, (self.x, 0, self.width, self.top), 2)
        pygame.draw.rect(screen, PIPE_GREEN, (self.x, self.top + self.gap, self.width, 600))
        pygame.draw.rect(screen, BLACK, (self.x, self.top + self.gap, self.width, 600), 2)

class FlappyGame:
    def __init__(self):
        pygame.init()

        pygame.mixer.init() 
        self.screen = pygame.display.set_mode((400, 600))
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        
        self.jump_sound = self.generate_beep(440, 0.1) 
        self.score_sound = self.generate_beep(880, 0.15) 
        
        self.reset_game()

    def generate_beep(self, frequency, duration):
        """Hata Giderildi: Sesi çift kanal (stereo) yapar."""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = np.sin(2 * np.pi * np.arange(n_samples) * frequency / sample_rate)
        buf *= np.linspace(1, 0, n_samples)
        buf = (buf * 32767).astype(np.int16)
        
        buf = np.column_stack((buf, buf)) 
        
        return pygame.sndarray.make_sound(buf)

    def reset_game(self):
        self.bird = Bird()
        self.pipes = [Pipe()]
        self.score, self.game_over = 0, False

    def run_frame(self):
        if self.game_over:
            self.display_menu()
            return

        self.screen.fill(SKY_BLUE)
        self.bird.update()
        self.bird.draw(self.screen)

        if self.pipes[-1].x < 180: self.pipes.append(Pipe())
        for pipe in self.pipes[:]:
            pipe.update()
            pipe.draw(self.screen)
            if (self.bird.x + 15 > pipe.x and self.bird.x - 15 < pipe.x + pipe.width):
                if (self.bird.y - 15 < pipe.top or self.bird.y + 15 > pipe.top + pipe.gap):
                    self.game_over = True
            if not pipe.passed and pipe.x < self.bird.x:
                self.score += 1
                pipe.passed = True
                self.score_sound.play() 
            if pipe.x < -70: self.pipes.remove(pipe)

        score_txt = self.font.render(f"SKOR: {self.score}", True, WHITE)
        self.screen.blit(score_txt, (15, 15))
        pygame.display.flip()

    def display_menu(self):
        overlay = pygame.Surface((400, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0,0))
        txt = self.font.render("YUMRUK YAP VE BASLA", True, WHITE)
        self.screen.blit(txt, (200 - txt.get_width()//2, 280))
        pygame.display.flip()

    def trigger_jump(self):
        if self.game_over: self.reset_game()
        else:
            self.bird.jump()
            self.jump_sound.play()