class SymbolTable:
    def __init__(self):
        """Creates a new empty symbol table"""
        self._statics = {}
        self._fields = {}
        self._args = {}
        self._vars = {}
        self._dicts = {'STATIC': self._statics, 'FIELD': self._fields, 'ARG': self._args, 'VAR': self._vars}

    def startSubroutine(self):
        """Starts a new subroutine scope (i.e. erases all names in the previous subroutine's scope.) """
        self._args.clear()
        self._vars.clear()

    def define(self, name, typeName, kind):
        """Defines a new identifier of a given name, type, and kind and assigns it a running index. STATIC
        and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope. """
        d = self._dicts.get(kind)
        d[name] = (typeName, len(d))

    def varCount(self, kind):
        """Returns the number of variables of the given kind already defined in the current scope. """
        return len(self._dicts.get(kind, {}))

    def get(self, name):
        for d in self._dicts:
            if name in self._dicts[d]:
                v = self._dicts[d][name]
                res = (d, v[0], v[1])
                return res
        return ('NOT_FOUND','NOT_FOUND','NOT_FOUND')

    def kindOf(self, name):
        """Returns the kindof the named identifier in the current scope. Returns NONEif the identifier is unknown
        in the current scope."""
        return self.get(name)[0]

    def typeOf(self, name):
        """Returns the typeof the named identifier in the current scope. """
        return self.get(name)[1]

    def indexOf(self, name):
        """Returns the index assigned to named identifier. """
        return self.get(name)[2]
