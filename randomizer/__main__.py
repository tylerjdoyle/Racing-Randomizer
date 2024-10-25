import asyncio

from game import Randomizer


if __name__ == "__main__":
    game = Randomizer()
    asyncio.run(game.main_loop())
    
