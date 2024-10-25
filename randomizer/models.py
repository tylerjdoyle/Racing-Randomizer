from pygame.math import Vector2
# from pygame.transform import rotozoom
import random

from utils import load_sprite

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
        split_name = name.split()
        self.name = split_name[0]
        self.initials = "{0}{1}".format(split_name[0][0], split_name[1][0])
        self.should_move = False
        super().__init__(position, load_sprite("circle"), random.uniform(1, 3))

        self.text = font.render(self.initials, False, self.TEXT_COLOR)
        self.textRect = self.text.get_rect()

    def draw(self, surface):
        super().draw(surface)
        self.textRect.center = self.position
        surface.blit(self.text, self.textRect)
        if self.finished_text is not None:
            self.finished_textRect.center = self.position + Vector2(self.radius * 2, 0)
            surface.blit(self.finished_text, self.finished_textRect)


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

    # TODO: add little animations later
    # def rotate(self, clockwise=True):
    #     dir = 1 if clockwise else -1
    #     angle = dir * self.MANUVERABILITY
    #     self.direction.rotate_ip(angle)

    # def draw(self, surface):
    #     angle = self.direction.angle_to(UP)
    #     rotated_surface = rotozoom(self.sprite, angle, 1.0)
    #     rotated_surface_size = Vector2(rotated_surface.get_size())
    #     blit_position = self.position - rotated_surface_size * 0.5
    #     surface.blit(rotated_surface, blit_position)

class Leader(Racer):
    DELAY = 10

    def __init__(self, name, position, font):
        self.counter = 0
        super().__init__(name, position, font)

    def accelerate(self):
        if self.should_move:
            if self.counter > self.DELAY:
                super().accelerate()

    def move(self):
        if self.should_move:
            if self.counter > self.DELAY:
                super().move()
            else:
                self.counter += 0.1