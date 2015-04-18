
class SymbolTable(object):
    def __init__(self):
        # Add default variables
        self.symbolDict = { 'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'SCREEN': 16384, 'KBD': 24576 }
        for i in range(16):
            self.symbolDict['R' + str(i)] = i

        self.counter = 16

    def addEntry(self, symbol, address=None):
        if address == None:
            address = self.counter
            self.counter += 1
        self.symbolDict[symbol] = address
        return address

    def getAddress(self, symbol):
        if symbol in self.symbolDict:
            return self.symbolDict[symbol]
        return self.addEntry(symbol)
