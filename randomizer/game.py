import pygame
import random
import asyncio
import sys
import pyperclip
from enum import Enum

from models import Racer, TextBox, SelectBox, TypeableTextBox
from utils import BLACK, WHITE, read_json

width, height = 1500, 750
grass_padding = 100 # 50 padding on top/bottom

FONT_SIZE = 18

BRICK_RED = (170, 74, 68)
GRASS = (19, 109, 21)

class GameState(Enum):
    INIT_SCREEN = 0
    INIT_INPUT = 1
    INPUT = 2
    SELECTION = 2.5 # Managed outside of advance_state
    END_INPUT = 3
    RACE_BEGIN = 4
    RACE_RUNNING = 5
    RACE_DONE = 6

    def advance_state(self):
        new_state = GameState(self.value + 1)
        print(f"Advancing state from {self} to {new_state}")
        return new_state
    
    def in_race(self):
        return self == GameState.RACE_BEGIN or self == GameState.RACE_RUNNING or self == GameState.RACE_DONE

INSTRUCTION_TEXT = {
    GameState.INPUT: ["CMD+E to load from list", "Press -> to start..."],
    GameState.SELECTION: ["Press <- to go back", "Press -> to select"],
    GameState.RACE_BEGIN: ["", "Press space to start race!"],
    GameState.RACE_DONE: ["", "Press R to restart race"]
}

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
        self.input = None
        self.text_box = TypeableTextBox(self.font, FONT_SIZE, (width/2, 20), ["Enter racers one per line (max 31). Empty lines will be ignored"])
        self.info_box = TextBox(self.font, FONT_SIZE, (width - 150, height - 40), INSTRUCTION_TEXT[GameState.INPUT])
        json = read_json("preloaded")
        print(json.items())
        self.preloaded_box = SelectBox(self.font, FONT_SIZE, (width/2, 20), json)
        self._advance_game_state()

    def _setup_race(self):
        surf_height = height - grass_padding
        padding = surf_height/self.num_people

        self._setup_ground(padding, surf_height)
        self._setup_racers(padding)
        print("here")
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
            racer = Racer(name, starting_pos, self.font, self.num_people)
            self.racers.append(racer)
        self.finished = []

    def _reset_race(self):
        self.game_state = GameState.RACE_BEGIN
        surf_height = height - grass_padding
        padding = surf_height/self.num_people
        self._setup_racers(padding)

    def _setup_finish_box(self, str):
        self.final_box = TextBox(self.font, FONT_SIZE, (width/2, 20), str, False)

    ### Input ###

    def _get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if self.game_state == GameState.INPUT:
                self.text_box.process_input(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        for text in self.text_box.text:
                            if text != "": # Make sure we have at least 1 valid input
                                self.input = [ input for input in list(filter(None, self.text_box.text)) if not input.isspace() ]
                                self.num_people = len(self.input)
                                if self.num_people > 0:
                                    print(f"INPUT {self.input}")
                                    self._advance_game_state()
                                    self.info_box.update_text(INSTRUCTION_TEXT[GameState.RACE_BEGIN], False)
                                    break
                    if (event.key == pygame.K_e) and (event.mod & (pygame.KMOD_META or pygame.KMOD_CTRL)):
                        self.game_state = GameState.SELECTION
                        self.info_box.update_text(INSTRUCTION_TEXT[GameState.SELECTION], False)
            if self.game_state == GameState.SELECTION:
                self.preloaded_box.process_input(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT:
                        self.text_box.update_text(self.preloaded_box.get_current_selection(), True)
                        self.game_state = GameState.INPUT
                        self.info_box.update_text(INSTRUCTION_TEXT[GameState.INPUT], False)
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_LEFT:
                        self.game_state = GameState.INPUT
                        self.info_box.update_text(INSTRUCTION_TEXT[GameState.INPUT], False)
            if self.game_state == GameState.RACE_BEGIN:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.game_state = self.game_state.advance_state()
                    for racer in self.racers:
                        racer.should_move = True
            if self.game_state == GameState.RACE_DONE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._reset_race()

    ### Game Logic ###
    
    def _process_game_logic(self):
        w, _ = self.screen.get_size()

        if self.game_state == GameState.INIT_INPUT:
            self._setup_input()
        elif self.game_state == GameState.END_INPUT:
            self._setup_race()
        elif self.game_state == GameState.RACE_RUNNING:
            sorted_racers = self.racers.copy()
            sorted_racers.sort(key=lambda x: x.position.x, reverse=True)
            for pos, racer in enumerate(sorted_racers):
                racer.accelerate(pos+1)
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
        self.info_box.update_text(INSTRUCTION_TEXT[GameState.RACE_DONE], False)
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
        if self.game_state == GameState.SELECTION:
            self.screen.fill(WHITE)
            self.preloaded_box.draw(self.screen)
            self.info_box.draw(self.screen)
        if self.game_state.in_race():
            self.screen.fill(GRASS)
            self.screen.blit(self.surf, self.surf.get_rect(center = self.screen.get_rect().center))
            for racer in self.racers:
                racer.draw(self.screen)
            if self.game_state == GameState.RACE_BEGIN:
                self.info_box.draw(self.screen)
        if self.game_state == GameState.RACE_DONE:
            self.final_box.draw(self.screen)
            self.info_box.draw(self.screen)
        pygame.display.update()
        pygame.display.flip()
        self.clock.tick(60)