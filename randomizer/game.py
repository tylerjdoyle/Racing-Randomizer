import pygame
import random

from models import Racer, Leader

TEAM = [
    "Test 1"
]
LEADERS = [

]
width, height = 1500, 750
num_people = len(TEAM)+len(LEADERS)

BLACK = (0,0,0)
WHITE = (255,255,255)
BRICK_RED = (170, 74, 68)
GRASS = (19, 109, 21)

class Randomizer: 
    def __init__(self):
        self.init_pygame()
        self.init_screen()
        self.clock = pygame.time.Clock()
        self.race_done = False

    def main_loop(self):
        while True:
            self._get_input()
            self._process_game_logic()
            self._draw()

    def init_pygame(self): 
        pygame.init()
        pygame.display.set_caption("AO Randomizer")

    def init_screen(self): 
        self.screen = pygame.display.set_mode((width, height))

        grass_padding = 100 # 50 padding on top/bottom
        surf_height = height - grass_padding
        thickness = 8
        self.surf = pygame.Surface((width, surf_height+thickness)) # Adds extra top+bottom padding
        self.surf.fill(BRICK_RED)
        padding = surf_height/num_people
        for i in range(num_people+1):
            # Lines are rendered from the center (top-center if even)
            adjustment = thickness / 2 - 1 if thickness % 2 == 0 else thickness / 2
            offset = i * padding + adjustment
            pygame.draw.line(self.surf, WHITE, (0, offset), (width, offset), width=thickness)
        self.len_from_edge = width / 15
        pygame.draw.line(self.surf, BLACK, (self.len_from_edge, 0), (self.len_from_edge, height), width=thickness) # start
        pygame.draw.line(self.surf, BLACK, (width-self.len_from_edge, 0), (width-self.len_from_edge, height), width=thickness) # finish

        self.font = pygame.font.Font('freesansbold.ttf', 18)
        # set up racers
        people = TEAM+LEADERS
        random.shuffle(people)
        self.racers = []
        for i in range(num_people):
            starting_pos = (self.len_from_edge / 2, (padding * i) + 50 + (padding / 2))
            name = people[i]
            if name in TEAM:
                racer = Racer(name, starting_pos, self.font)
            else:
                racer = Leader(name, starting_pos, self.font)
            self.racers.append(racer)
        self.finished = []

    def _get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                quit()
            if not self.race_done and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: 
                for racer in self.racers:
                    racer.should_move = True

    def _process_game_logic(self):
        w, _ = self.screen.get_size()
        if not self.race_done:
            for racer in self.racers:
                racer.accelerate()
                racer.move()
                if racer.is_finished(w - self.len_from_edge + racer.radius, len(self.finished)):
                    self.finished.append(racer)
            if len(self.finished) == num_people:
                self._finish_race()

    def _finish_race(self):
        self.race_done = True
        for i in range(len(self.finished)): 
            finisher = self.finished[i]
            print("{0}. {1}".format(i+1, finisher.name))
        
        self.blit_text(self.surf, self._create_finish_str(), (20,20), self.font)

    # Copied from https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
    def blit_text(self, surface, text, pos, font):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, True, BLACK, WHITE)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def _create_finish_str(self):
        str = ''
        for i in range(len(self.finished)): 
            finisher = self.finished[i]
            str += "{0}. {1}".format(i+1, finisher.name)
            if i < len(self.finished):
                str += "\n\r"
        return str

    def _draw(self):
        self.screen.fill(GRASS)
        self.screen.blit(self.surf, self.surf.get_rect(center = self.screen.get_rect().center))
        for racer in self.racers:
            racer.draw(self.screen)
        pygame.display.update()
        pygame.display.flip()
        self.clock.tick(60)