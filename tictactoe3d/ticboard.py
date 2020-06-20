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

        self.generateFrame() #Clears area and generates frame
        
    def addTuples(self,tuple1,tuple2):
        return ((i + i1) for i, i1 in zip(tuple1,tuple2))
    
    def generateFrame(self):
        mcworld = self._world
        #Makes a rectangle around the play area
        mcworld.setBlocks(*(self.addTuples((0,0,0), (-1,-1,-1))),       
            *(self.addTuples(self._dimensions, (1,1,1))), 42) 
        
        #Make a hole in the x-axis
        mcworld.setBlocks(*(self.addTuples((0,0,0), (-1,0,0))),       
            *(self.addTuples(self._dimensions, (1,0,0))), 0) 

        #Make a hole in the y-axis
        mcworld.setBlocks(*(self.addTuples((0,0,0), (0,-1,0))),       
            *(self.addTuples(self._dimensions, (0,1,0))), 0) 

        #Make a hole in the z-axis
        mcworld.setBlocks(*(self.addTuples((0,0,0), (0,0,-1))),       
            *(self.addTuples(self._dimensions, (0,0,1))), 0) 
        

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
            block = self._world.getBlock(*self.translate_cords(x,y,z))
            if block != self._blocks[val] and block in self._blocks.values():
                if updatedblock:
                    raise Exception(f'World has more than one different block at {self.translate_cords(x,y,z)}')
                updatedblock = (x,y,z,block)
        x,y,z = updatedblock[:3]
        if updatedblock[3] == self.getblockturn():
            self[x,y,z] = self._turn
            self.switchturn()
            self.checkwinner(x,y,z)

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
        source = self.source
        return (x + source['x'], y + source['y'], z + source['z'])


    def traverse_directions(self,x,y,z):
        def wallhit(x,y,z,direction):
            nextIterX = x + direction[0]
            nextIterY = y + direction[1]
            nextIterZ = z + direction[2]
            if nextIterX < 0 or nextIterX >= self._dimensions[0]:
                return True
            if nextIterY < 0 or nextIterY >= self._dimensions[1]:
                return True
            if nextIterZ < 0 or nextIterZ >= self._dimensions[2]:
                return True
            return False
                        


        def traverse_direction(x,y,z,direction):
            playersymbol = self[x,y,z]
            if wallhit(x,y,z,direction):
                return 0
            count = -1
            cursymbol = self[ ( (i + i1) for i,i1 in zip((x,y,z), direction)) ]
            while (count < self.winlen) and (cursymbol == playersymbol) and (wallhit(x,y,z,direction) == False):
                count += 1
                x,y,z = (i + i1 for i,i1 in zip((x,y,z), direction))
                cursymbol = self[x,y,z]
            return count
        

        playersymbol = self[x,y,z] 
        for direction in directions:
            if traverse_direction(x,y,z,direction[0]) + traverse_direction(x,y,z,direction[1]) >= self.winlen:
                return playersymbol
        return False
            




    def checkwinner(self,x,y,z):
        '''Private method. Sets self.winner to winner'''
        self.winner = self.traverse_directions(x,y,z)

    def getwinner(self):
        return self.winner
    

    


