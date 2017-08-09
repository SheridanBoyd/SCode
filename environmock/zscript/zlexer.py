LETTERS = [chr(j) for j in range(ord('a'), ord('z')+1)]+[chr(j) for j in range(ord('A'), ord('Z')+1)]
NUMBERS = [str(i) for i in range(0, 10)]
ADDMIN = ['+', '-']
MULDIV = ['*', '/']
EXP = ['^']
EQ = ['=']
NL = ['\r', '\n', ';']
WS = [' ']
RB = [')']
LB = ['(']
LLB = ['[']
LRB = [']']
SEP = [',']
FUNC = ['==']
COMP = ['?', '!', '<', '>']
VALIDCOMP = ['?=', '!=', '<', '<=', '>', '>=']
WSHIDDEN = True


def lexer(s):
    i = 0
    terminals = []
    while i < len(s):
        term = None
        if s[i] in NUMBERS or s[i] == '.':
            i, term = isnumber(s, i)

        elif s[i] in LETTERS:
            i, term = isvar(s, i)

        elif s[i] in EQ:
            i, term = isequal(s, i)

        elif s[i] in ADDMIN:
            i, term = isaddmin(s, i)

        elif s[i] in MULDIV:
            i, term = ismuldiv(s, i)

        elif s[i] in EXP:
            i, term = isexp(s, i)

        elif s[i] in RB:
            i, term = isrb(s, i)

        elif s[i] in LB:
            i, term = islb(s, i)

        elif s[i] in LLB:
            i, term = isllb(s, i)

        elif s[i] in LRB:
            i, term = islrb(s, i)

        elif s[i] in SEP:
            i, term = issep(s, i)

        elif s[i] in COMP:
            i, term = isbool(s, i)

        elif s[i] in WS:
            if WSHIDDEN:
                i += 1
            else:
                i, term = iswhitespace(s, i)

        elif s[i] in NL:
            i, term = isnewline(s, i)

        else:
            i, term = error(s, i)

        if term is not None:
            terminals.append(term)

    return terminals


def isint(s, i):
    t = ''
    while i < len(s) and s[i] in NUMBERS:
        t += s[i]
        i += 1

    return i, t


def isnumber(s, i):
    term = ''
    i, t = isint(s, i)
    term += t
    try:
        s[i]
    except IndexError:
        return i, ('INT', term)
    else:
        if s[i] == '.':
            term += '.'
            i += 1
            i, t = isint(s, i)
            term += t
            return i, ('FLOAT', term)
        else:
            return i, ('INT', term)


def isvar(s, i):
    v = ''
    while i < len(s) and (s[i] in LETTERS or s[i] in NUMBERS):
        v += s[i]
        i += 1

    return i, ('CHAR', v)


def isbool(s, i):
    if s[i]+s[i+1] in VALIDCOMP:
        return i+2, ('COMP', s[i]+s[i+1])
    elif s[i] in VALIDCOMP:
        return i+1, ('COMP', s[i])
    else:
        return error(s, i)


def isequal(s, i):
    if s[i]+s[i+1] in FUNC:
        return i+2, ('FUNC', s[i]+s[i+1])
    else:
        return i+1, ('EQ', s[i])


def isexp(s, i):
    return i+1, ('EXP', s[i])


def isaddmin(s, i):
    return i+1, ('ADDMIN', s[i])


def ismuldiv(s, i):
    return i+1, ('MULDIV', s[i])


def isrb(s, i):
    return i+1, ('RB', s[i])


def islb(s, i):
    return i+1, ('LB', s[i])


def isllb(s, i):
    return i+1, ('LLB', s[i])


def islrb(s, i):
    return i+1, ('LRB', s[i])


def issep(s, i):
    return i+1, ('SEP', s[i])


def iswhitespace(s, i):
    return i+1, ('WS', s[i])


def isnewline(s, i):
    return i+1, ('NL', s[i])


def error(s, i):
    e = ''
    while i < len(s) and not (s[i] in LETTERS or
                              s[i] in NUMBERS or
                              s[i] == '.' or
                              s[i] in EQ or
                              s[i] in EXP or
                              s[i] in ADDMIN or
                              s[i] in MULDIV or
                              s[i] in RB or
                              s[i] in LB or
                              s[i] in LLB or
                              s[i] in LRB or
                              s[i] in SEP or
                              s[i] in WS or
                              s[i] in NL or
                              s[i] in VALIDCOMP or
                              s[i]+s[i+1] in VALIDCOMP):

        e += s[i]
        i += 1

    return i, ('ERROR', e)
