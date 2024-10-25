# import sys module
import pygame
import sys
import asyncio

from game import Randomizer  
  
game = Randomizer()    
asyncio.run(game.main_loop())