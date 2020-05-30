# mcpi-3d-tic-tac-toe
MCPI 3d tic tac toe with N x N x N matrix

Instructions.
1. Start minecraft server
2. "import tictacetoe3d"
3. Initialize mc_board

Basics. 
-play(x,y,z) Place block at x,y,z
-updateworld() Updates the minecraft world to represent the internal matrix
-updateboard() Updates the board to represent the minecraft world (ignores non air and player blocks)
-getwinner() Returns winner
