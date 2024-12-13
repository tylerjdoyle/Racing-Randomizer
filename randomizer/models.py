from pygame.math import Vector2
from pygame.sprite import Sprite
# from pygame.transform import rotozoom

import pygame
import pyperclip

import random
import time

from utils import load_sprite, BLACK, UP

class GameObject: 
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = velocity

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self):
        self.position = self.position + (self.velocity, 0)

class Racer(GameObject):
    ACCELERATION = random.uniform(0, 0.3)
    LOW_VARIATION = random.uniform(0, 2)
    HIGH_VARIATION = random.uniform(7, 9)

    TEXT_COLOR = (1, 1, 1)

    def __init__(self, name, position, font):
        self.finished_text = None
        self.finished_textRect = None
        self.font = font
        self.name = name
        self.initials = self._get_short_name(name)
        self.should_move = False
        # self.direction = Vector2(0, 0)
        super().__init__(position, load_sprite("circle"), random.uniform(1, 3))

        self.text = font.render(self.initials, False, self.TEXT_COLOR)
        self.textRect = self.text.get_rect()

    def _get_short_name(self, name):
        split_name = name.split()
        if len(split_name) > 1:
            return f"{split_name[0][0]}{split_name[1][0]}"
        elif len(split_name[0]) > 1:
            return f"{split_name[0][0]}{split_name[0][1]}"
        else:
            return f"{split_name[0][0]}"

    def draw(self, surface):
        super().draw(surface)
        self.textRect.center = self.position
        surface.blit(self.text, self.textRect)
        # angle = self.direction.angle_to(UP)
        # rotated_surface = rotozoom(self.sprite, angle, 1.0)
        # rotated_surface_size = Vector2(rotated_surface.get_size())
        # blit_position = self.position - rotated_surface_size * 0.5
        # surface.blit(rotated_surface, blit_position)
        if self.finished_text is not None:
            self.finished_textRect.center = self.position + Vector2(self.radius * 2, 0)
            surface.blit(self.finished_text, self.finished_textRect)

    # Scale based on distance from end
    def accelerate(self):
        if self.should_move:
            rand_num = random.uniform(0, 10)
            if rand_num > self.HIGH_VARIATION:
                self.velocity += self.ACCELERATION
            elif rand_num < self.LOW_VARIATION:
                self.velocity -= self.ACCELERATION
                self.velocity = max(self.velocity, 1)
            # else nothing

    def move(self):
        if self.should_move:
            super().move()      
            
    def is_finished(self, finish_pos, num_finishers):
        if self.should_move and self.position.x > finish_pos:
            self.should_move = False
            self.finished_text = self.font.render(str(num_finishers+1), False, self.TEXT_COLOR)
            self.finished_textRect = self.text.get_rect()
            return True

    # def rotate(self, clockwise=True):
    #     dir = 1 if clockwise else -1
    #     angle = dir * self.MANUVERABILITY
    #     self.direction.rotate_ip(angle)

class TextBox(Sprite):
    def __init__(self, font, font_size, center, input_text=[], show_cursor=False):
        Sprite.__init__(self)
        self.text = [""]
        self.current_line = 0
        self.font = font
        self.font_size = font_size
        self.root = center
        self.show_cursor = show_cursor

        # Create initial input text
        self.update_text(input_text, False)

    def update_text(self, new_text, editable):
        if not editable:
            self.images = []
            for i in range(len(new_text)):
                text = new_text[i]
                image = self.font.render(text, False, BLACK)
                rect = image.get_rect()
                rect.center = self._get_offset(i)
                self.images.append((image, rect))
        else:
            self.text = new_text
            self.current_line = len(new_text)-1
            self.update()

    def _get_offset(self, row):
        return (self.root[0], self.root[1] + (row * (self.font_size + 5)))

    def update(self):
        self.images = []
        for row, line in enumerate(self.text):
            img = self.font.render(line, False, BLACK)
            rect = img.get_rect()
            rect.center = self._get_offset(row)
            self.images.append((img, rect))

    def process_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.current_line != 0:
                    self.current_line -= 1
            if event.key == pygame.K_DOWN:
                if self.current_line < len(self.images) - 1:
                    self.current_line += 1
    
    def draw(self, surface):
        for (image, rect) in self.images:
            surface.blit(image, rect)
        current_rect = self.images[self.current_line][1]
        if self.show_cursor:
            self.cursor = pygame.Rect(current_rect.topright, (3, current_rect.height))
            if time.time() % 1 > 0.5:
                pygame.draw.rect(surface, BLACK, self.cursor)

class TypeableTextBox(TextBox):
    def __init__(self, font, font_size, center, input_text=[], show_cursor=True):
        super().__init__(font, font_size, center, input_text, show_cursor)

    def _add_text(self, text):
        for char in text:
            if self.current_line >= 32:
                continue
            if char == "\n":
                self.current_line += 1
                self.text.append("")
            else:
                self.text[self.current_line] += char
            if len(self.text[self.current_line]) == 100:
                self.current_line += 1
                self.text.append("")
        self.update()
    
    def _remove_char(self):
        if len(self.text) != 1 and len(self.text[self.current_line]) == 0:
            self.text.pop()
            self.current_line -= 1
        else:
            self.text[self.current_line] = self.text[self.current_line][:-1]
        self.update()

    def process_input(self, event):
        if event.type == pygame.TEXTINPUT:
            self._add_text(event.text)
        elif event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_v) and (event.mod & (pygame.KMOD_META or pygame.KMOD_CTRL)):
                try: 
                    self._add_text(pyperclip.paste())
                except:
                    print("No clipboard on Linux")
            if event.key == pygame.K_BACKSPACE:
                self._remove_char()
            if event.key == pygame.K_RETURN:
                self._add_text("\n")
        return super().process_input(event)
    
class SelectBox(TextBox):
    def __init__(self, font, font_size, center, selections_json):
        self.selections = selections_json
        super().__init__(font, font_size, center, [x[0] for x in self.selections.items()], True)
    
    def get_current_selection(self):
        options = [x[1] for x in self.selections.items()]
        return options[self.current_line]