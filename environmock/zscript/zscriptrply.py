from rply import *
from zsyntaxtree import *

# 'NUMBER', 'IDENT',
# 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'DEF', 'EQ', 'COMP',
# 'RB', 'LB', 'LLB', 'LRB', 'SEP', 'NL'

#pg = ParserGenerator(['NUMBER', 'IDENT', 'EQ', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'RB', 'LB', 'NL'],
pg = ParserGenerator(['NUMBER', 'IDENT', 'STRING', 'EQ', 'DEF', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'RB', 'LB', 'COM', 'NXT', 'NXV', 'TRC', 'SPC', 'NEG'],#, 'LLB', 'LRB', 'SEP'],

                      precedence=[
                                  ('left', ['EQ', 'DEF']),
                                  ('left', ['ADD', 'SUB']),
                                  ('left', ['UNI']),
                                  ('left', ['MUL', 'DIV', 'ADJ']),
                                  ('left', ['EXP'])])


@pg.production('line : printresult')
@pg.production('line : setvar')
@pg.production('line : setfunc')
@pg.production('line : nextfunc')
@pg.production('line : trace')
def line(p):
    return p[0]


@pg.production('line : ')
def empty(p):
    return NOP()


@pg.production('printresult : expression')
def result(p):
    return Print(p[0])


@pg.production('expression : NUMBER')
def val(p):
    p = p[0].getstr()
    return Number(float(p))


@pg.production('expression : STRING')
def str(p):
    p = p[0].getstr()[1:-1]  # Gets out string and takes out quotes
    return String(p)


@pg.production('expression : IDENT SPC expression')
def func(p):
    f = p[0].getstr()
    i = p[2]
    return Function(f, i)


@pg.production('expression : IDENT')
def var(p):
    v = p[0].getstr()
    return Variable(v)


# @pg.production('expression : ADD expression')
# @pg.production('expression : SUB expression')
# def uni(p):
#     t1 = p[0].getstr()
#     t2 = p[1]
#     return Value(t2, t1)


@pg.production('setvar : IDENT EQ expression')
@pg.production('setfunc : IDENT DEF expression')
@pg.production('setfunc : IDENT NXV DEF expression')
@pg.production('expression : expression ADD expression')
@pg.production('expression : expression SUB expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
@pg.production('expression : expression EXP expression')
def expression(p):
    l = p[0]
    r = p[-1]
    o = p[-2].gettokentype()
    if o == 'ADD':
        r = Add(l,r)
    elif o == 'SUB':
        r = Sub(l, r)
    elif o == 'MUL':
        r = Mul(l, r)
    elif o == 'DIV':
        r = Div(l, r)
    elif o == 'EXP':
        r = Exp(l, r)
    elif o == 'EQ':
        r = SetVar(l.getstr(), r)
    elif o == 'DEF':
        cur = p[1].gettokentype() != 'NXV'
        r = SetDef(l.getstr(), r, cur=cur)
    return r


# @pg.production('listbit : expression')
# @pg.production('listbit : listbit SEP listbit')
# def listbit(p):
#     if len(p) > 1:
#         return list(p[0]).append(p[2])
#     else:
#         return p
#
#
# @pg.production('expression : LLB listbit LRB')
# def makelist(p):
#     return List(p[1])

@pg.production('expression : IDENT NXV')
def nxv(p):
    v = p[0].getstr()
    return NextVariable(v)


@pg.production('nextfunc : NXT NUMBER')
def nxt(p):
    n = p[1].getstr()
    if float(n) == int(n):
        return Next(int(n))
    else:
        raise ValueError('The number after "next" must be an integer, %s' % n)


@pg.production('trace : TRC IDENT')
def trc(p):
    v = p[1].getstr()
    return Trace(v)


@pg.production('expression : LB expression RB')
def bra(p):
    return p[1]


@pg.production('expression : LB expression COM expression RB')
def cplx(p):
    x = p[1]
    y = p[3]
    return Vector(x, y)


@pg.production('expression : expression expression', precedence='ADJ')
def impmul(p):
    return Mul(p[0],p[1])


@pg.production('expression : NEG expression', precedence='UNI')
def neg(p):
    return Value(p[1], '-')


parser = pg.build()

if __name__ == '__main__':
    pass

#    next variable       n_
#    delta
#    differential        n'
#    string              "string"
