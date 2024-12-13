from pygame.image import load
from pygame.math import Vector2
import json

BLACK = (0,0,0)
WHITE = (255,255,255)
UP = Vector2(0, -1)

def load_sprite(name, with_alpha=True):
    path = f"./assets/sprites/{name}.png"
    loaded_sprite = load(path)
    if with_alpha:
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()
    
def read_json(name):
    with open(f"./assets/{name}.json", 'r') as file:
        data = json.load(file)
        return data
    return None