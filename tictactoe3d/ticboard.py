from numpy import array
from collections.abc import Iterable
from mcpi.minecraft import Minecraft


class mc_board:
    def __init__(self, dimensions : Iterable, winlen : int, mcworld, blocks, source_as_ppos = True) -> 'mc_board':
        '''dimensions: (x,y,z), winlen, mcworld, blocks: (1st player block, 2nd player block) '''
        assert winlen < max(dimensions), 'winlen too high'
        self._board = array([[ [0 for i in range(dimensions[0])] 
                                                        for i1 in range(dimensions[2]) ]
                                                        for i2 in range(dimensions[1]) ], dtype = int)
        self._world = mcworld
        self._turn = 1
        self.winlen = winlen
        self._blocks = { 0 : 0,
                         1 : blocks[0],
                         2 : blocks[1]}
        self.source = {}
        self._dimensions = dimensions
        if source_as_ppos:
            self.set_source_at_ppos()
        else:
            self.source['x'] = 0 
            self.source['y'] = 0 
            self.source['z'] = 0 
        
        


    def __iter__(self):

        return iter(self._board)

    def __getitem__(self, cords):
        x,y,z = cords
        return self._board[y,z,x]       #Array access is in the form "(y,z,x)" or layer, row, index

    def __setitem__(self, cords, val):

        assert val in (0,1,2,'x','o'), "invalid input"
        if val == 'x':
            val = 1
        elif val == 'o':
            val = 2
        
        x,y,z = cords
        self._board[y,z,x] = val
        self.switchturn()
            
        self.checkwinner(x,y,z)
        self.updateblock(x,y,z,val)
        if self.winner:
            print(f'{self._blocks[self.winner]} won!')
    
    def __repr__(self):
        return repr(self._board)


    def switchturn(self):
        if self._turn == 1:
            self._turn = 2
        else:
            self._turn = 1

    def getmatrix(self):
        return self._board
    
    def setsource(self,x,y,z):
        '''Manual source adjustment'''
        self.source['x'] = x
        self.source['y'] = y
        self.source['z'] = z
    
    def set_source_at_ppos(self):
        '''Change the source position of the board to player position'''
        x,y,z = self._world.player.getTilePos()
        self.setsource(x,y,z)

    def check_valid(self,x,y,z):
        assert self[x,y,z] == 0, 'spot has been placed'
        assert x < self._dimensions[0], f'X is too large, max is {self._dimensions[0]}'
        assert y < self._dimensions[1], f'Y is too large, max is {self._dimensions[1]}'
        assert z < self._dimensions[2], f'Z is too large, max is {self._dimensions[2]}'

    def play(self,x,y,z):
        '''Check one spot at player turn'''
        self.check_valid(x,y,z)
        self[x,y,z] = self._turn


    def updateboard(self):
        '''Checks minecraft world and updates the internal array(ignores non air and player blocks)'''
        updatedblock = None
        for x,y,z,val in self._enumiter():
            block = self._world.getBlock(x,y,z)
            if block != self._blocks[val] and block in self._blocks.values():
                if updatedblock:
                    raise Exception(f'World has more than one different block at {self.translate_cords(x,y,z)}')
                updatedblock = (x,y,z,block)

        if updatedblock[3] != self.getblockturn():
            self[x,y,z] = updatedblock[3]
            self.switchturn()
            self.checkwinner()

        else:
            raise Exception(f'Incorrect turn at {self.translate_cords(x,y,z)}')

    def getblockturn(self):
        return self._blocks[self._turn]
        
    def _enumiter(self):
        '''Helper method to iterate with x,y,z,val'''
        return ( (x,y,z,val) for y, layer in enumerate(self._board)
                             for z, row in enumerate(layer)
                             for x, val in enumerate(row))
    def draw(self):
        '''wrapper for updateworld()'''
        self.updateworld()

    def undraw(self):
        '''redraw area with air'''
        for x,y,z,val in self._enumiter():
            self.updateblock(x,y,z,0)

    def updateworld(self):
        '''Updates minecraft world to array'''
        for x,y,z,val in self._enumiter():
            self.updateblock(x,y,z,val)

    def updateblock(self,x,y,z,blockval):
        '''Helper method to update block using matrix cords'''
        source = self.source
        self._world.setBlock(*self.translate_cords(x,y,z),
                                         self._blocks[blockval])
    


    directions = (((-1, -1, -1), (1, 1, 1)) , ((-1, -1, 0), (1, 1, 0)) , ((-1, -1, 1), (1, 1, -1)),
                  ((-1, 0, -1) , (1, 0, 1)) , ((-1, 0, 0) , (1, 0, 0)) , ((-1, 0, 1) , (1, 0, -1)),
                  ((-1, 1, -1) , (1, -1, 1)), ((-1, 1, 0) , (1, -1, 0)), ((-1, 1, 1) , (1, -1, -1)),
                  ((0, -1, -1) , (0, 1, 1)) , ((0, -1, 0) , (0, 1, 0)) , ((0, -1, 1) , (0, 1, -1)),
                  ((0, 0, -1)  , (0, 0, 1))) #All possible directions
    
    def translate_cords(self,x,y,z):
        '''Translates matrix cords into minecraft cords'''
        return (x + source['x'], y + source['y'], z + source['z'])

    def _find_possible_wins(self,x,y,z):
        playersymbol = self[x,y,z]
        def validate_direction(direction):
            if self[ ( (i + i1) for i,i1 in zip((x,y,z), direction)) ]  == playersymbol:
                return True
            return False
        valid_directions = []
        currentdirections = []
        for direction1,direction2 in self.directions:
            if validate_direction(direction1):
                currentdirections.append(direction1)

            if validate_direction(direction2):
                currentdirections.append(direction2)

            valid_directions.append(tuple(currentdirections))
        return valid_directions



    def traverse_directions(self,x,y,z,directions):
        def traverse_direction(direction,playersymbol):
            nonlocal x,y,z
            count = -1
            cursymbol = self[ ( (i + i1) for i,i1 in zip((x,y,z), direction)) ]
            while count < self.winlen and cursymbol == playersymbol:
                count += 1
                x,y,z = (i + i1 for i,i1 in zip((x,y,z), direction))
                cursymbol = self[x,y,z]
            return count
        
        playersymbol = self[x,y,z] 
        for direction in directions:
            if len(direction) == 1:
                if traverse_direction(direction[0],playersymbol) > self.winlen:
                    return playersymbol
            elif len(direction) == 2:
                if traverse_direction(direction[0],playersymbol) + traverse_direction(direction[1],playersymbol) > self.winlen:
                    return playersymbol
        return False
            




    def checkwinner(self,x,y,z):
        '''Private method. Sets self.winner to winner'''
        self.winner = self.traverse_directions(x,y,z, self._find_possible_wins(x,y,z))

    def getwinner(self):
        return self.winner
    

    


