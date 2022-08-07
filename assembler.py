# Custom MIPS Assembler written in Python3
# Author: utchchhwas

from sys import argv
import os
import re


OPCODES = {
    'or':   '0000',
    'subi': '0001',
    'ori':  '0010',
    'sub':  '0011',
    'add':  '0100',
    'lw':   '0101',
    'j':    '0110',
    'sll':  '0111',
    'sw':   '1000',
    'addi': '1001',
    'srl':  '1010',
    'beq':  '1011',
    'nor':  '1100',
    'and':  '1101',
    'andi': '1110',
    'bneq': '1111'
}

REGISTERS = {
    '$zero':    '0000',
    '$t0':      '0001',
    '$t1':      '0010',
    '$t2':      '0011',
    '$t3':      '0100',
    '$t4':      '0101',
    '$sp':      '0110'
}


def parseLabel(line):
    return re.match(r'([_a-zA-Z][_a-zA-Z0-9]*):', line)


def parse(line):

    g = re.match(r'(or|sub|add|nor|and)[ ]+(\$t[0-4]|\$zero|\$sp),[ ]*(\$t[0-4]|\$zero|\$sp),[ ]*(\$t[0-4]|\$zero|\$sp)', line)
    if g:
        return g.groups()

    g = re.match(r'(subi|ori|addi|andi|sll|srl)[ ]+(\$t[0-4]|\$zero|\$sp),[ ]*(\$t[0-4]|\$zero|\$sp),[ ]*([-]?[0-9]+)', line)
    if g:
        return g.groups()

    g = re.match(r'(lw|sw)[ ]+(\$t[0-4]|\$zero|\$sp),[ ]*([0-9]+)\((\$t[0-4]|\$zero|\$sp)\)', line)
    if g:
        return g.groups()

    g = re.match(r'(beq|bneq)[ ]+(\$t[0-4]|\$zero|\$sp),[ ]*(\$t[0-4]|\$zero|\$sp),[ ]*([_a-zA-Z][_a-zA-Z0-9]+)', line)
    if g:
        return g.groups()

    g = re.match(r'(j)[ ]+([_a-zA-Z][_a-zA-Z0-9]*)', line)
    if g:
        return g.groups()

    g =  re.match(r'([_a-zA-Z][_a-zA-Z0-9]*):', line)
    if g:
        return g.groups()

    raise RuntimeError('Unknown instruction format')


def getRTypeFormat(opcode, desReg, srcReg1, srcReg2):
    fmt = [OPCODES[opcode], REGISTERS[srcReg1], REGISTERS[srcReg2], REGISTERS[desReg]]
    return fmt


def getITypeFormat(opcode, desReg, srcReg, const):
    constVal = int(const)

    if constVal < -8 or constVal >= 8:
        raise RuntimeError('Immediate value overflow')
        
    if constVal < 0:
        constVal += (1 << 32)

    fmt = [OPCODES[opcode], REGISTERS[srcReg], REGISTERS[desReg], '{0:04b}'.format(constVal)[-4:]]
    return fmt


def getJTypeFormat(opcode, jmpAddr):
    jmpAddrVal = int(jmpAddr)

    if jmpAddrVal >= 256:
        raise RuntimeError('Jump address overflow')

    fmt = [OPCODES[opcode], '{0:08b}'.format(jmpAddrVal)[-8:], '0000']
    return fmt


def main():
    if len(argv) != 2:
        print("Invalid usage: python assembler.py [inputFile]")
        exit(1)
    
    try:
        asmFile = open(argv[1], 'r')
    except FileNotFoundError:
        print(f'Error: {argv[1]} not found')
        exit(1)

    lines = asmFile.read().splitlines()

    binOutFile = open('output.bin', 'wb')

    print("Running Assembler...", end='\n\n')

    labels = {}
    lineNo = 0
    for line in lines:
        line = line.strip()
        tk = parseLabel(line)
        if tk:
            labels[tk[1]] = lineNo
        else:
            lineNo += 1

    error = False
    lineNo = 0
    for i, line in enumerate(lines):
        line = line.strip()
        try:
            tk = parse(line.strip())

            isLabel = False
            fmt = None
            if tk[0] in {'or', 'sub', 'add', 'nor', 'and'}:
                fmt = getRTypeFormat(tk[0], tk[1], tk[2], tk[3])

            elif tk[0] in {'subi', 'ori', 'addi', 'andi', 'sll', 'srl'}:
                fmt = getITypeFormat(tk[0], tk[1], tk[2], tk[3])

            elif tk[0] in {'lw', 'sw'}:
                fmt = getITypeFormat(tk[0], tk[1], tk[3], tk[2])

            elif tk[0] in {'beq', 'bneq'}:
                jumpLabel = tk[3]

                if jumpLabel not in labels:
                    raise RuntimeError('Unrecognized label')

                jumpOffset = labels[jumpLabel] - (lineNo + 1)

                fmt = getITypeFormat(tk[0], tk[1], tk[2], str(jumpOffset))

            elif tk[0] in {'j'}:
                jumpLabel = tk[1]

                if jumpLabel not in labels:
                    raise RuntimeError('Unrecognized label')

                jumpAddr = labels[jumpLabel]
                
                fmt = getJTypeFormat(tk[0], str(jumpAddr))
                
            else:
                isLabel = True

            if not isLabel:
                fmtStr = ' '.join(item for item in fmt)
                fmtBytes = int(fmtStr.replace(' ', ''), 2).to_bytes(2, byteorder='big')

                print(f'#{lineNo:02d}: {line} => {fmtStr} \ {fmtBytes.hex()}', end='\n\n')

                binOutFile.write(fmtBytes)
                lineNo += 1

        except RuntimeError as e:
            print(f'Error on line {i+1}: {e} [{line}]', end='\n\n')
            error = True


    asmFile.close()
    binOutFile.close()

    if error:
        os.remove('output.bin')
        print("Assembling unsuccessful ❌")
        exit(1)
    else:
        print("Assembling successful ✅")


if __name__ == '__main__':
    main()
