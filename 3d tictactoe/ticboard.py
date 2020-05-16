from numpy import array
from collections.abc import Iterable
from mcpi.minecraft import Minecraft


class mc_board:
    def __init__(self, dimensions : Iterable, winlen : int, mcworld) -> 'mc_board':
        '''dimensions: (x,y,z), winlen'''
        self._board = array([ [0 for i in dimensions[0]] for i1 in dimensions[1] ]
                                                          for i2 in dimensions[2] )
        self._world = mcworld
        self._turn = 'x'
        
    def __getitem__(self, x,y,z):
        return self._board[y,z,x]       #Array access is in the form "(y,z,x)" or layer, row, index

    def __setitem__(self, val, x,y,z, updateworld = False):
        assert val not in (0,1,2,'x','y'), "invalid input"
        self._board[y,z,x] = val
        if updateworld:
            self.check_winner(y,z,x)
            self.update_block(y,z,x)
    
    def __repr__(self):
        return repr(self._board)

    

        
        
