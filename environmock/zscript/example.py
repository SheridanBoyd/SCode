from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from zlexerrply import lexer
from zscript.rply import BaseBox
from zscript.rply import ParserGenerator


# 'NUMBER', 'IDENT',
# 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'FUNC', 'EQ', 'COMP',
# 'RB', 'LB', 'LLB', 'LRB', 'SEP', 'NL'

class Base(BaseBox):
    def __call__(self, env):
        pass


class NOP(Base):
    pass


class Value(Base):
    def __init__(self, value, posmin):
        self.value = value
        self.posmin = posmin

    def __call__(self, env):
        if self.posmin == '-':
            r = - self.value(env)
        else:
            r = + self.value(env)
        return r


class Number(Base):
    def __init__(self, val):
        self.val = val

    def __call__(self, env):
        return self.val


# class List(Base):
#     def __init__(self, listbit):
#         self.listbit = listbit
#
#     def __call__(self, env):
#         bit = [bit(env) for bit in self.listbit]
#         return np.array(bit)
#

class Variable(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env):
        return env['value'][self.var](env)


class SetVar(Base):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def __call__(self, env):
        env['value'][self.var] = Number(self.val(env))


class SetFunc(Base):
    recur = defaultdict(list)

    def __init__(self, var, func):
        self.var = var
        self.func = func
        def z(): return Number(1)
        recur = {'value': defaultdict(z), 'function': defaultdict(z)}
        self.func(recur)
        self.recur[self.var] = list(recur['function'].keys())
        self.findfuncs(self.var)


    def __call__(self, env):
        if self.var in env['function']:
            raise Exception('Cannot Redefine The Function "%s"' % self.var)
        else:
            env['function'][self.var] = self.func

    def findfuncs(self, var):
        funcs = self.recur[var]
        if self.var in funcs:
            raise Exception('Recursion happened when defining the function "%s"' % self.var)
        else:
            for func in self.recur[var]:
                self.findfuncs(func)


class Next(Base):
    def __init__(self, loops):
        self.loops = loops


    def __call__(self, env):
        tenv = env['trace']

        for i in xrange(self.loops):
            newvalues = env['value'].copy()
            for var, eq in env['function'].items():
                v = Number(eq(env))
                newvalues[var] = v
            env['value'] = newvalues
            yield [env['value'][var](env) for var in tenv]

class NextVariable(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env, current=False):
        return env['function'][self.var](env)


class Trace(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env):
        env['trace'].append(self.var)


class BinOp(Base):
    def __init__(self, l, r):
        self.l = l
        self.r = r


class Add(BinOp):
    def __call__(self, env):
        return self.l(env) + self.r(env)

    # def compile(self, env):
    #     if self.l.constant and self.r.constant:
    #         constant = self.l(env) + self.r(env)
    #         def constantfunc():
    #             return constant
    #         return constantfunc
    #     else:
    #         def variablefunc():
    #             return self.l(env) + self.r(env)
    #         return variablefunc()


class Sub(BinOp):
    def __call__(self, env):
        return self.l(env) - self.r(env)


class Mul(BinOp):
    def __call__(self, env):
        return self.l(env) * self.r(env)


class Div(BinOp):
    def __call__(self, env):
        return self.l(env) / self.r(env)


class Exp(BinOp):
    def __call__(self, env):
        return self.l(env) ** self.r(env)


#pg = ParserGenerator(['NUMBER', 'IDENT', 'EQ', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'RB', 'LB', 'NL'],
pg = ParserGenerator(['NUMBER', 'IDENT', 'EQ', 'FUNC', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'RB', 'LB', 'NXT', 'NXV', 'TRC'],#, 'LLB', 'LRB', 'SEP'],

                      precedence=[
                                  ('left', ['EQ', 'FUNC']),
                                  ('left', ['ADD', 'SUB']),
                                  ('left', ['MUL', 'DIV']),
                                  ('left', ['EXP'])
                                  ])


@pg.production('program : printresult')
@pg.production('program : setvar')
@pg.production('program : setfunc')
@pg.production('program : nextfunc')
@pg.production('program : trace')
def program(p):
    return p[0]


@pg.production('program : ')
def empty(p):
    return NOP()


@pg.production('printresult : expression')
def result(p):
    return p[0]


@pg.production('expression : NUMBER')
def val(p):
    p = p[0].getstr()
    return Number(float(p))


@pg.production('expression : IDENT')
def var(p):
    v = p[-1].getstr()
    return Variable(v)


@pg.production('expression : ADD expression')
@pg.production('expression : SUB expression')
def uni(p):
    t1 = p[0].getstr()
    t2 = p[1]
    return Value(t2, t1)


@pg.production('setvar : IDENT EQ expression')
@pg.production('setfunc : IDENT NXV FUNC expression')
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
    elif o == 'FUNC':
        r = SetFunc(l.getstr(), r)
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
    return Trace(p[1].getstr())


@pg.production('expression : LB expression RB')
def bra(p):
    return p[1]


def newenv():
    return {'function': {}, 'value': {}, 'trace': []}


def printgen(gen):
    x = 0
    r = []
    for i in gen:
        x += 1
        r.append(i)
        if x % 1000 == 0:
            print(i)
    print(i)
    return r


def testparser(test):
    env = newenv()
    SetFunc.recur
    plotting = []
    for instr in test.splitlines():
        tokens = lexer.lex(instr)
        pro = parser.parse(tokens)
        out = pro(env)
        p = out
        try:
            plotting = printgen(out)
        except Exception as error:
            print(p)
    showenv(env)
    return plotting


def showenv(env):
    fenv = env['function']
    venv = env['value']
    tenv = env['trace']

    print('env values')
    for var, eq in venv.items():
        print(var+':', eq(env))

    print('env functions')
    for var, eq in fenv.items():
        print(var+':', eq(env))

    print('env trace')
    for var in tenv:
        print(var)


if __name__ == '__main__':
    parser = pg.build()
    # tokens = lexer.lex('a_ == - 1 + (2) * 5 ^ 3')
    # pro = parser.parse(tokens)
    # env = {'function': {}, 'value': {'a': Add(Number(4), Variable('b')), 'b': Number(7)}}
    # print(pro(env))
    # print(env)
    # test = """a = 1
    # b = 2
    # c = 1
    # d2_ == b^2 - 4*a*c
    # x1_ == -b + d2_^0.5
    # x2_ == -b - d2_^0.5
    # a
    # b
    # c
    # d2_
    # x1_
    # x2_"""
    # testparser(test)
    #
    # ftest = '''
    # n1 = 1
    # n2 = 1
    # n1_ == n2
    # n2_ == n1 + n2
    # next 4
    # n2
    # n2_'''
    # test= '''a = 0
    # a_ == a + 1
    # next 100'''
    # testparser(ftest)
    # #ballp = [-0.109, -0.643]

    spring = '''
    ballm = 0.402
    ballpx = -0.109
    ballpy = -0.643
    ballvx = 0.2
    ballvy = -0.1
    springx = -0.007
    springy = -0.0050
    t = 0
    dt = (1/210)/10
    g = 9.8
    ks = 6.83
    L0 = 0.123
    Lx_ == ballpx-springx
    Ly_ == ballpy-springy
    Lmag_ == (Lx_^2 + Ly_^2)^0.5
    Lhx_ == Lx_/Lmag_
    Lhy_ == Ly_/Lmag_
    s_ == Lmag_-L0
    Fgravy_ == (ballm*-g)
    Fspringx_ == (-ks*s_)*Lhx_
    Fspringy_ == (-ks*s_)*Lhy_
    Fnetx_ == Fspringx_
    Fnety_ == Fspringy_ + Fgravy_
    ballvx_ == ballvx + Fnetx_/ballm*dt
    ballvy_ == ballvy + Fnety_/ballm*dt
    ballpx_ == ballpx + ballvx_*dt
    ballpy_ == ballpy + ballvy_*dt
    t_ == t + dt
    t
    trace t
    trace ballpx
    trace ballpy
    next 11550
    '''

    #make this work - need comments and 'mag' function
    spring2 = '''
    # mathematical constants
        xh == 1
        yh == (-1)^(1/2)
    # constant values for this simulation
        Mball == 0.402
        Pspring == -0.007*xh - 0.0050*yh
        dt == (1/210)
        g == 9.8
        ks == 6.83
        L0 == 0.123
    # initial values
        Pball = -0.109*xh - 0.643*yh
        Vball = 0.18*xh
        t = 0
    # calculated values - current values, not 'next' values
        L == Pball-Pspring
        Lmag == mag L  #!!!
        Lh == L/Lmag
        stretch == Lmag - L0
        Fs == (-ks*stretch)*Lh
        Fg == (Mball*-g)
        Fnet == Fs + Fg
        Vball == p / Mball
    # next time step (create 'next' values)
        p_ == p + dt*Fnet
        Pball_ == Pball + Vball_*dt
        t_ == t + dt
    # run simulation
        trace t
        trace Pball
        next 1950
        '''
    plotting = np.array(testparser(spring))
    plotting = plotting.T
    plt.plot(plotting[1], plotting[2])
    #plt.scatter(0,0)
    print(SetFunc.recur)

    X =[-0.109, -0.08, -0.045, -0.004, 0.036, 0.071, 0.097, 0.108, 0.104, 0.088, 0.057, 0.019, -0.021, -0.062, -0.094, -0.115, -0.12, -0.113, -0.091, -0.06, -0.02, 0.023, 0.058, 0.089, 0.105, 0.107, 0.094, 0.068, 0.034, -0.008, -0.047, -0.084, -0.107, -0.121, -0.116, -0.098, -0.071, -0.034, 0.008, 0.048, 0.08, 0.101, 0.108, 0.1, 0.078, 0.046, 0.007, -0.034, -0.07, -0.1, -0.116, -0.119, -0.106, -0.081, -0.045, -0.007, 0.036, 0.069, 0.096, 0.111, 0.105, 0.086, 0.06, 0.022, -0.016, -0.057, -0.088, -0.113, -0.12, -0.113, -0.093, -0.061, -0.02, 0.022, 0.058, 0.088, 0.105, 0.108, 0.096, 0.072, 0.037, -0.003, -0.042, -0.078, -0.104, -0.119, -0.118, -0.103, -0.074, -0.038, 0.004, 0.043, 0.078, 0.102, 0.11, 0.103]
    Y =[-0.643, -0.665, -0.686, -0.708, -0.732, -0.747, -0.759, -0.763, -0.754, -0.739, -0.719, -0.697, -0.678, -0.662, -0.651, -0.646, -0.654, -0.669, -0.689, -0.711, -0.731, -0.748, -0.758, -0.762, -0.754, -0.741, -0.722, -0.698, -0.678, -0.66, -0.651, -0.648, -0.655, -0.672, -0.688, -0.711, -0.729, -0.747, -0.759, -0.761, -0.753, -0.739, -0.718, -0.697, -0.676, -0.66, -0.652, -0.649, -0.654, -0.672, -0.688, -0.709, -0.731, -0.749, -0.757, -0.761, -0.754, -0.738, -0.719, -0.698, -0.678, -0.667, -0.655, -0.649, -0.655, -0.668, -0.687, -0.711, -0.732, -0.748, -0.754, -0.761, -0.757, -0.739, -0.719, -0.697, -0.68, -0.664, -0.655, -0.651, -0.659, -0.671, -0.69, -0.71, -0.729, -0.743, -0.756, -0.758, -0.75, -0.737, -0.718, -0.699, -0.677, -0.662, -0.654, -0.652]
    plt.plot(X,Y)
    plt.show()


#    next variable       n_
#    delta
#    differential        n'
#    string              "string"