import pygame
import random
import asyncio
import sys
import pyperclip
from enum import Enum

from models import Racer, TextBox
from utils import BLACK, WHITE

width, height = 1500, 750
grass_padding = 100 # 50 padding on top/bottom

FONT_SIZE = 18

BRICK_RED = (170, 74, 68)
GRASS = (19, 109, 21)

class GameState(Enum):
    INIT_SCREEN = 0
    INIT_INPUT = 1
    INPUT = 2
    END_INPUT = 3
    RACE_BEGIN = 5
    RACE_RUNNING = 6
    RACE_DONE = 7

    def advance_state(self):
        if self == GameState.INIT_SCREEN:
            new_state = GameState.INIT_INPUT
        elif self == GameState.INIT_INPUT:
            new_state = GameState.INPUT
        elif self == GameState.INPUT:
            new_state = GameState.END_INPUT
        elif self == GameState.END_INPUT:
            new_state = GameState.RACE_BEGIN
        elif self == GameState.RACE_BEGIN:
            new_state = GameState.RACE_RUNNING
        elif self == GameState.RACE_RUNNING or self == GameState.RACE_DONE:
            new_state = GameState.RACE_DONE
        print(f"Advancing state from {self} to {new_state}")
        return new_state
    
    def in_race(self):
        return self == GameState.RACE_BEGIN or self == GameState.RACE_RUNNING or self == GameState.RACE_DONE

class Randomizer: 
    def __init__(self):
        self.game_state = GameState.INIT_SCREEN
        self.init_pygame()
        self.init_screen()
        self.clock = pygame.time.Clock()

    def _advance_game_state(self):
        self.game_state = self.game_state.advance_state()

    ### Main Loop ###

    async def main_loop(self):
        while True:
            self._get_input()
            self._process_game_logic()
            self._draw()
            await asyncio.sleep(0)

    ### Initialization ###

    def init_pygame(self): 
        pygame.init()
        pygame.display.set_caption("Racing Randomizer")

    def init_screen(self): 
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
        self._advance_game_state()
    
    ### Setup helpers ###

    def _setup_input(self):
        self.text_box = TextBox(self.font, FONT_SIZE, (width/2, 20), ["Enter racers one per line (max 31). Empty lines will be ignored"])
        self.info_box = TextBox(self.font, FONT_SIZE, (width - 100, height - 20), ["Press -> to start..."], False)
        self._advance_game_state()

    def _setup_race(self):
        surf_height = height - grass_padding
        padding = surf_height/self.num_people

        self._setup_ground(padding, surf_height)
        self._setup_racers(padding)
        self._advance_game_state()

    def _setup_ground(self, padding, surf_height):
        thickness = 8
        self.surf = pygame.Surface((width, surf_height+thickness)) # Adds extra top+bottom padding
        self.surf.fill(BRICK_RED)
        padding = surf_height/self.num_people
        for i in range(self.num_people+1):
            # Lines are rendered from the center (top-center if even)
            adjustment = thickness / 2 - 1 if thickness % 2 == 0 else thickness / 2
            offset = i * padding + adjustment
            pygame.draw.line(self.surf, WHITE, (0, offset), (width, offset), width=thickness)
        self.len_from_edge = width / 15
        pygame.draw.line(self.surf, BLACK, (self.len_from_edge, 0), (self.len_from_edge, height), width=thickness) # start
        pygame.draw.line(self.surf, BLACK, (width-self.len_from_edge, 0), (width-self.len_from_edge, height), width=thickness) # finish

    def _setup_racers(self, padding):
        people = self.input
        random.shuffle(people)
        self.racers = []
        for i in range(self.num_people):
            starting_pos = (self.len_from_edge / 2, (padding * i) + 50 + (padding / 2))
            name = people[i]
            racer = Racer(name, starting_pos, self.font)
            self.racers.append(racer)
        self.finished = []

    def _setup_finish_box(self, str):
        self.final_box = TextBox(self.font, FONT_SIZE, (width/2, 20), str, False)

    ### Input ###

    def _get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if self.game_state == GameState.INPUT:
                self.input = self.text_box.process_input(event)
                if self.input != None:
                    self.input = [ input for input in list(filter(None, self.input)) if not input.isspace() ]
                    self.num_people = len(self.input)
                    if self.num_people > 0:
                        print(f"INPUT {self.input}")
                        self._advance_game_state()
            if self.game_state == GameState.RACE_BEGIN:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.game_state = self.game_state.advance_state()
                    for racer in self.racers:
                        racer.should_move = True

    ### Game Logic ###
    
    def _process_game_logic(self):
        w, _ = self.screen.get_size()

        if self.game_state == GameState.INIT_INPUT:
            self._setup_input()
        elif self.game_state == GameState.END_INPUT:
            self._setup_race()
        elif self.game_state == GameState.RACE_RUNNING:
            for racer in self.racers:
                racer.accelerate()
                racer.move()
                if racer.is_finished(w - self.len_from_edge + racer.radius, len(self.finished)):
                    self.finished.append(racer)
            if len(self.finished) == self.num_people:
                self._finish_race()

    def _finish_race(self):
        for i in range(len(self.finished)): 
            finisher = self.finished[i]
            print("{0}. {1}".format(i+1, finisher.name))
        
        str = self._create_finish_str()
        try:
            pyperclip.copy(str)
        except:
            print("No clipboard on Linux")
        self._setup_finish_box(str)
        self.game_state = self.game_state.advance_state()

    def _create_finish_str(self):
        str = []
        for i in range(len(self.finished)): 
            finisher = self.finished[i]
            str.append("{0}. {1}".format(i+1, finisher.name))
        return str

    ### Drawing ###

    def _draw(self):
        if self.game_state == GameState.INPUT:
            self.screen.fill(WHITE)
            self.text_box.draw(self.screen)
            self.info_box.draw(self.screen)
        if self.game_state.in_race():
            self.screen.fill(GRASS)
            self.screen.blit(self.surf, self.surf.get_rect(center = self.screen.get_rect().center))
            for racer in self.racers:
                racer.draw(self.screen)
        if self.game_state == GameState.RACE_DONE:
            self.final_box.draw(self.screen)
        pygame.display.update()
        pygame.display.flip()
        self.clock.tick(60)