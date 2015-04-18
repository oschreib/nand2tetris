
class HackCode(object):
    ''' Helper class for parsing C instructions.
    '''
    @staticmethod
    def dest(mnemonic):
        ''' Returns the binary code of the dest mnemonic (3 bits)'''
        ret = '1' if 'A' in mnemonic else '0'
        ret += '1' if 'D' in mnemonic else '0'
        ret += '1' if 'M' in mnemonic else '0'
        if ret.count('1') != len(mnemonic):
            raise Exception("Invalid dest: {0}".format(mnemonic))
        return ret

    @staticmethod
    def comp(mnemonic):
        ''' Returns the binary code of the comp mnemonic (7 bits)'''
        possibleComps = {   '0': '0101010', '1': '0111111', '-1': '0111010','D': '0001100',
                            'A': '0110000', '!D': '0001101', '!A': '0110001', '-D': '0001111',
                            '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
                            'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
                            'D&A': '0000000', 'D|A': '0010101', 'M': '1110000', '!M': '1110001',
                            '-M': '1110011', 'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
                            'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000', 'D|M': '1010101'}
        if mnemonic not in possibleComps:
            raise Exception("Invalid comp instruction: {0}".format(mnemonic))
        return possibleComps[mnemonic]

    @staticmethod
    def jump(mnemonic):
        ''' Returns the binary code of the jump mnemonic (3 bits)'''
        jumps = ['', 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']
        try:
            return '{:03b}'.format(jumps.index(mnemonic))
        except:
            raise Exception("Unknown jump: {0}".format(mnemonic))
