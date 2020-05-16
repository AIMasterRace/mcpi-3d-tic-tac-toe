from numpy import array
from collections.abc import Iterable
from mcpi.minecraft import Minecraft


class mc_board:
    def __init__(self, dimensions : Iterable, winlen : int, mcworld, blocks, source_as_ppos = True) -> 'mc_board':
        '''dimensions: (x,y,z), winlen, mcworld, blocks: (1st player block, 2nd...) '''
        self._board = array([[ [0 for i in range(dimensions[0])] 
                                                        for i1 in range(dimensions[1]) ]
                                                        for i2 in range(dimensions[2]) ], dtype = int)
        self.world = mcworld
        self._turn = 0
        self._blocks = { 0 : 0,
                         1 : blocks[0],
                         2 : blocks[1]}
        self.source = {}
        if source_as_ppos:
            self.source = self.set_source_at_ppos()
        else:
            self.source['x'] = 0 
            self.source['y'] = 0 
            self.source['z'] = 0 
        


    def __iter__(self):

        return (val for layer in self._board
                    for row in layer
                    for val in row    )

    def __getitem__(self, x,y,z):
        return self._board[y,z,x]       #Array access is in the form "(y,z,x)" or layer, row, index

    def __setitem__(self, val, x,y,z, updateworld = False):
        assert val not in (0,1,2,'x','y'), "invalid input"
        if val == 'x':
            val = 1
        elif val == 'y':
            val = 2

        self._board[y,z,x] = val

        self.switchturn()
            
        if updateworld:
            self.winner = self.checkwinner(x,y,z)
            self.updateblock(x,y,z)
            if self.winner:
                print(f'{self._blocks[self.winner]} won!')
    
    def __repr__(self):
        return repr(self._board)

    def switchturn(self):
        if self._turn == 0:
            self._turn = 1
        else:
            self._turn = 0

    def getmatrix(self):
        return self._board
    
    def setsource(self,x,y,z):
        self.source['x'] = x
        self.source['y'] = y
        self.source['z'] = z
    
    def set_source_at_ppos(self):
        self.source['x'],
        self.source['y'],
        self.source['z'] = self._world.player.getPos()

    
    def updateworld(self):
        source = self.source
        for y, layer in enumerate(self._board):
            for z, row in enumerate(layer):
                for x, val in enumerate(row):
                    self._world.setBlock(x + source['x'],
                                         y + source['y'],
                                         z + source['z'],
                                         self._blocks[val])
    def updateblock(self,x,y,z):
        self._world.setBlock(x,y,z,self._blocks[self._board[y,z,x]])
    


    directions = (((-1, -1, -1), (1, 1, 1)) , ((-1, -1, 0), (1, 1, 0)) , ((-1, -1, 1), (1, 1, -1)),
                  ((-1, 0, -1) , (1, 0, 1)) , ((-1, 0, 0) , (1, 0, 0)) , ((-1, 0, 1) , (1, 0, -1)),
                  ((-1, 1, -1) , (1, -1, 1)), ((-1, 1, 0) , (1, -1, 0)), ((-1, 1, 1) , (1, -1, -1)),
                  ((0, -1, -1) , (0, 1, 1)) , ((0, -1, 0) , (0, 1, 0)) , ((0, -1, 1) , (0, 1, -1)),
                  ((0, 0, -1)  , (0, 0, 1))) #All possible directions


    def _find_possible_wins(self,x,y,z):
        playersymbol = self[x,y,z]
        def validate_direction(direction):
            if self[*(i + i1 for i,i1 in zip((x,y,z), direction))] == playersymbol:
                return True
            return False
        valid_directions = []
        for direction in self.directions:
            if validate_direction(direction):
                valid_directions.append(direction)

        return valid_directions



    def traverse_directions(self,x,y,z,directions):
        def traverse_direction(direction,playersymbol):
            count = 0
            cursymbol = self[*(i + i1 for i,i1 in zip((x,y,z), direction))]
            while count < self.winlen and cursymbol == playersymbol:
                count += 1
                x,y,z = *(i + i1 for i,i1 in zip((x,y,z), direction))
                cursymbol = self[x,y,z]
            return count
        
        playersymbol = self[x,y,z]
        for direction in directions:
            if len(direction) == 1:
                if traverse_direction(direction) > self.winlen:
                    return playersymbol
            else:
                if traverse_direction(direction[0]) + traverse_direction(direction[1]) > self.winlen:
                    return playersymbol
        return False
            




    def checkwinner(self,x,y,z):
        return traverse_directions(x,y,z, self._find_possible_wins(x,y,z))

    


