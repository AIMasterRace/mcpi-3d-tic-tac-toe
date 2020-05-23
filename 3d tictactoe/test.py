import ticboard
import mcpi.minecraft
world = mcpi.minecraft.Minecraft.create()
blocks = (57,12)
dimensions = (5,6,7)
winlen = 5
board = ticboard.mc_board(dimensions, winlen, world, blocks)

for i in range(5):
    board[0,i,0] = 1
