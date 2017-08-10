from rply import *
from zsyntaxtree import *

# 'NUMBER', 'IDENT',
# 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'DEF', 'EQ', 'COMP',
# 'RB', 'LB', 'LLB', 'LRB', 'SEP', 'NL'

#pg = ParserGenerator(['NUMBER', 'IDENT', 'EQ', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'RB', 'LB', 'NL'],
pg = ParserGenerator(['NUMBER', 'IDENT', 'STRING', 'EQ', 'DEF', 'AND', 'OR', 'NOT', 'COMP', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'RB', 'LB', 'COM', 'NXT', 'NXV', 'TRC', 'SPC', 'NEG'],#, 'LLB', 'LRB', 'SEP'],

                      precedence=[
                                  ('left', ['CONVERT']),
                                  ('left', ['EQ', 'DEF']),
                                  ('left', ['AND']),
                                  ('left', ['OR']),
                                  ('left', ['NOT']),
                                  ('left', ['COMP']),
                                  ('left', ['ADD', 'SUB']),
                                  ('left', ['UNI']),
                                  ('left', ['MUL', 'DIV']),
                                  ('left', ['ADJ']),
                                  ('left', ['EXP'])])


# @pg.production('program : opspc', precedence='END')
# @pg.production('program : opspc line opspc', precedence='CONVERT')
# def program(p):
#     if len(p) > 1:
#         return p[1]
#     else:
#         return NOP()
#
#
# @pg.production('opspc : SPC')
# @pg.production('opspc : ', precedence='END')
# def opspc(p):
#     return NOP()


@pg.production('line : printresult')
@pg.production('line : setvar')
@pg.production('line : setfunc')
@pg.production('line : nextfunc')
@pg.production('line : trace')
def line(p):
    return p[0]


@pg.production('line : ')
def none(p):
    return NOP()


@pg.production('printresult : expression', precedence='CONVERT')
def result(p):
    return Print(p[0])


@pg.production('expression : NUMBER', precedence='CONVERT')
def val(p):
    p = p[0].getstr()
    return Number(float(p))


@pg.production('expression : STRING', precedence='CONVERT')
def str(p):
    p = p[0].getstr()[1:-1]  # Gets out string and takes out quotes
    return String(p)


@pg.production('expression : IDENT SPC expression', precedence='EXP')
def func(p):
    f = p[0].getstr()
    i = p[2]
    return Function(f, i)


@pg.production('expression : IDENT', precedence='CONVERT')
def var(p):
    v = p[0].getstr()
    return Variable(v)


# @pg.production('expression : ADD expression')
# @pg.production('expression : SUB expression')
# def uni(p):
#     t1 = p[0].getstr()
#     t2 = p[1]
#     return Value(t2, t1)

@pg.production('expression : NOT expression', precedence='NOT')
def notbool(p):
    return Not(p[1])


@pg.production('setvar : IDENT EQ expression', precedence='EQ')
@pg.production('setfunc : IDENT DEF expression', precedence='DEF')
@pg.production('setfunc : IDENT NXV DEF expression', precedence='DEF')
@pg.production('expression : expression AND expression', precedence='AND')
@pg.production('expression : expression OR expression', precedence='OR')
@pg.production('expression : expression COMP expression', precedence='COMP')
@pg.production('expression : expression ADD expression', precedence='ADD')
@pg.production('expression : expression SUB expression', precedence='SUB')
@pg.production('expression : expression MUL expression', precedence='MUL')
@pg.production('expression : expression DIV expression', precedence='DIV')
@pg.production('expression : expression EXP expression', precedence='EXP')
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
    elif o == 'COMP':
        comp = p[-2].getstr()
        r = Compare(l, r, comp)
    elif o == 'AND':
        r = And(l, r)
    elif o == 'OR':
        r = Or(l, r)
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

@pg.production('expression : IDENT NXV', precedence='EXP')
def nxv(p):
    v = p[0].getstr()
    return NextVariable(v)


@pg.production('nextfunc : NXT NUMBER', precedence='EXP')
def nxt(p):
    n = p[1].getstr()
    if float(n) == int(n):
        return Next(int(n))
    else:
        raise ValueError('The number after "next" must be an integer, %s' % n)


@pg.production('trace : TRC IDENT', precedence='EXP')
def trc(p):
    v = p[1].getstr()
    return Trace(v)


@pg.production('expression : LB expression RB', precedence='EXP')
def bra(p):
    return p[1]


@pg.production('expression : LB expression COM expression RB', precedence='EXP')
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
