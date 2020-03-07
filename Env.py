from asyncore import file_dispatcher

import pandas as pd

import plotly.offline as py #visualization

# add desired grid

class Env:
    def __init__(self, filename):
        with open(filename, "r") as f:
            # I'm assuming the file could be sparse

            lines = [l for l in f.read().splitlines() if l != ""]
            index = lines.index("scrambled_image")


            assert lines[0] == "unscrambled_image"
            assert lines[1][0:5] == "size="
            size = int(lines[1][5:])
            desiredState = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
            for l in lines[2:index]:
                # add to state
                eIndex = l.index("=")
                pos = l[:eIndex]
                posStr = pos.split(",")
                x = int(posStr[0])
                y = int(posStr[1])
                z = int(posStr[2])

                color = l[eIndex+1:].strip("\"")

                desiredState[x][y][z] = color

            assert lines[index] == "scrambled_image"
            assert lines[index+1][0:5] == "size="
            dSize = int(lines[index+1][5:])
            assert dSize == size
            state = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
            for l in lines[index+2:]:
                # add to state
                eIndex = l.index("=")
                pos = l[:eIndex]
                posStr = pos.split(",")
                x = int(posStr[0])
                y = int(posStr[1])
                z = int(posStr[2])

                color = l[eIndex + 1:].strip("\"")

                state[x][y][z] = color

            self.state = state
            self.dState = desiredState
            self.state_dataFrame = self.convert_to_dataframe(state)
            self.dState_dataFrame = self.convert_to_dataframe(desiredState)
            self.s = size

    def stateEquals(self, mem):
        return self.state == mem

    def done(self):
        return self.state == self.dState

    def blockAt(self, x, y):
        for z in reversed(range(self.s)):
            if self.state[x][y][z] != "":
                return self.state[x][y][z], z
        return None # default could be "", -1
    
    def desiredBlockAt(self, x, y):
        for z in reversed(range(self.s)):
            if self.state[x][y][z] != "":
                return self.dState[x][y][z], z
        return None

    def getSize(self):
        return self.s

    def addBlock(self, x, y, tuple):
        color = tuple[0]
        z = tuple[1]

        # check that x, y, z is in the grid area
        xIn = x >= 0 and x < self.s
        yIn = y >= 0 and y < self.s
        zIn = z >= 0 and z < self.s
        if not(xIn and yIn and zIn):
            print("can't add block becasue (x, y, z) is out of bounds")
            return None

        # check if the block will be floating
        bAt = self.blockAt(x,y)
        if bAt is None:
            existingZ = -1
        else:
            _, existingZ = bAt
        if z != existingZ + 1:
            if z <= existingZ:
                print("Can't place block beneath another block", x, y, z, existingZ)
                return None
            print("warning, you are placing a floating block")

            # check that the block will have at least 1 neighbor to support it
            leftN = False if x == 0 else self.state[x-1][y][z] != ""
            rightN = False if x == self.s - 1 else self.state[x+1][y][z] != ""
            upN = False if y == self.s - 1 else self.state[x][y+1][z] != ""
            downN = False if y == 0 else self.state[x][y-1][z] != ""

            if (not leftN) and (not rightN) and (not upN) and (not downN):
                print("No neightbors to support")
                return None

        # add block in
        self.state[x][y][z] = color
        return True # success

    def takeBlock(self, x, y):
        bAt = self.blockAt(x,y)

        # check that there is a block there
        if bAt is None:
            print("can't take block, there isn't a block to take")
            return None

        color = bAt[0]
        z = bAt[1]

        # check that one of the sides is empty
        leftN = False if x == 0 else self.state[x - 1][y][z] != ""
        rightN = False if x == self.s - 1 else self.state[x + 1][y][z] != ""
        upN = False if y == self.s - 1 else self.state[x][y + 1][z] != ""
        downN = False if y == 0 else self.state[x][y - 1][z] != ""
        if leftN and rightN and upN and downN:
            print("can't take block, all of its neighbors are full")
            return None

        self.state[x][y][z] = ""
        return color#, z
    
    def convert_to_dataframe(self, State):
        df = pd.DataFrame(columns=['X', 'Y', 'Z', 'RGB'])
        for x in range(len(State)):
            for y in range(len(State[x])):
                for z in range(len(State[x][y])):
                    if State[x][y][z] == '':
                        df = df.append({'X': x, 'Y': y, 'Z': z, 'RGB': None}, ignore_index=True)
                    else:
                        RGB_values = State[x][y][z].split('_')
                        df = df.append({'X': x, 'Y': y, 'Z': z, 'RGB': 'rgb({0},{1},{2})'.format(RGB_values[0],RGB_values[1],RGB_values[2])}, ignore_index=True)
        #print(df.head)
        return df

    def plot_state(self):
        pass