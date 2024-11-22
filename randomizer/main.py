import pyperclip
import asyncio

from game import Randomizer  
  
game = Randomizer()    
asyncio.run(game.main_loop())