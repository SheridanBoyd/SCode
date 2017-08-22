import operator as op
import random as rdm
from collections import defaultdict

from .rply.token import BaseBox


class ZWarning(Warning):
    currentwarnings = []
    def __init__(self, message):
        self.message = message
        self.currentwarnings.append(message)

    @classmethod
    def clearwarnings(cls):
        cls.currentwarnings = []


class Base(BaseBox):
    def __call__(self, env, flag=None):
        pass

    def __repr__(self):
        return ''


class NOP(Base):
    pass


class Print(Base):
    def __init__(self, eq):
        self.eq = eq

    def __call__(self, env, flag=None):
        yield self.eq(env, flag)

    def __repr__(self):
        return repr(self.eq)


class Literal(Base):
    precedence = 100
    def __init__(self, val):
        self.val = val

    def __call__(self, env, flag=None):
        return self.val

    def __repr__(self):
        tp = type(self.val)
        if tp == str:
            return repr(String(self.val))
        elif tp == float:
            return repr(Number(self.val))
        elif tp == bool:
            return repr(Boolean(self.val))
        elif tp == complex:
            return repr(Vector(self.val.real, self.val.imag))
        else:
            raise TypeError('The type: ' + str(tp) + 'is not a valid Literal')


class String(Literal):
    def __init__(self, val):
        assert type(val) == str
        Literal.__init__(self, val)

    def __repr__(self):
        return '"{0}"'.format(self.val)


class Number(Literal):
    def __init__(self, val):
        assert type(val) == float
        Literal.__init__(self, val)

    def __repr__(self):
        return str(self.val)


class Boolean(Literal):
    def __init__(self, val):
        assert type(val) == bool
        Literal.__init__(self, val)

    def __repr__(self):
        return str(self.val)


class Random(Literal):
    def __init__(self):
        pass

    def __call__(self, env, flag=None):
        return rdm.random()


class Vector(Literal):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        Literal.__init__(self, None)

    def __call__(self, env, flag=None):
        val = self.val
        if self.val is None:
            x = self.x(env, flag)
            y = self.y(env, flag)
            if flag is None:
                self.val = complex(x, y)
            val = complex(x, y)
        return val

    def __repr__(self):
        return '({0}, {1})'.format(self.x, self.y)


class Variable(Base):
    precedence = 100
    def __init__(self, var):
        self.var = var

    def __call__(self, env, flag=None):
        if flag is not None:
            return env[self.var, flag]
        else:
            return env[self.var, 'cur']

    def __repr__(self):
        return self.var


class SetVar(Base):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def __call__(self, env, flag=None):
        env[self.var, 'val'] = Literal(self.val(env, 'nxt'))

    def __repr__(self):
        return self.var + ' := ' + repr(self.val)


class SetDef(Base):
    recur = defaultdict(list)

    def __init__(self, var, func, cur=True):
        self.var = var
        self.func = func
        self.cur = cur

    def __call__(self, env, flag=None):
        if self.cur:
            env[self.var, 'cur'] = self.func
        else:
            env[self.var, 'nxt'] = self.func

    def __repr__(self):
        if self.cur:
            return self.var + ' = ' + repr(self.func)
        else:
            return self.var + '_ = ' + repr(self.func)


class Function(Base):
    precedence = 10
    def __init__(self, func, inpt):
        self.func = func
        self.inpt = inpt

    def __call__(self, env, flag=None):
        function = env[self.func, 'func']
        return function(self.inpt, flag)

    def __repr__(self):
        inpt = repr(self.inpt)
        if self.precedence > self.inpt.precedence:
            inpt = '(' + inpt + ')'
        return self.func + ' ' + inpt


class Next(Base):
    def __init__(self, loops):
        self.loops = loops

    def __call__(self, env, flag=None):
        tenv = env.object['trc']
        genv = env.object['gph']
        nenv = env.object['nxt']
        vars = tenv
        for x, y in genv:
            if x not in vars:
                vars.append(x)
            if y not in vars:
                vars.append(y)

        dictdata = lambda vars: {var: env[var, 'cur'] for var in vars}

        def loop():
            newvalues = env.object['val'].copy()
            for var, eq in nenv.items():
                try:
                    v = Literal(eq(env, flag))
                except Exception as e:
                    args = ', '.join([i for i in e.args if type(i) in (str,)])
                    error = e.__class__()
                    error.message = args + '\nThere was an error while updating "%s"\n%s_ = %s' % (var, var, eq)
                    raise error
                newvalues[var] = v
            env.object['val'] = newvalues
            c = dictdata(vars)
            return c

        def nextdata():
            def n1():
                yield dictdata(vars)
                for i in range(self.loops):
                    yield loop()
            def n2():
                def i():
                    yield dictdata(vars)
                    while True:
                        yield loop()
                yield i()
            if self.loops > 0:
                return n1()
            else:
                return n2()

        self.nextdata = nextdata()
        return nextdata()

    def __repr__(self):
        return 'next ' + str(self.loops)


class NextVariable(Base):
    precedence = 100
    def __init__(self, var):
        self.var = var

    def __call__(self, env, flag=None):
        return env[self.var, 'nxt']

    def __repr__(self):
        return self.var + '_'


class Trace(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env, flag=None):
        env.tracevar(self.var)

    def __repr__(self):
        return 'trace ' + self.var


class Graph(Base):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __call__(self, env, flag=None):
        env.graphvars(self.x, self.y)

    def __repr__(self):
        r = 'graph ' + self.x
        if self.y is not None:
            r += ' ' + self.y
        return r


class BinOp(Base):
    ops = {'^': (op.pow, 8),
           '*': (op.mul, 7),
           '/': (op.truediv, 6),
           '-': (op.sub, 5),
           '+': (op.add, 5),
           '==': (op.eq, 4),
           '!=': (op.ne, 4),
           '<=': (op.le, 4),
           '>=': (op.ge, 4),
           '<': (op.lt, 4),
           '>': (op.gt, 4),
           'and': (op.and_, 2),
           'or': (op.or_, 1)}

    def __init__(self, l, r, com):
        self.l = l
        self.r = r
        self.symbol = com.strip()
        self.com, self.precedence = self.ops[self.symbol]

    def __call__(self, env, flag=None):
        return self.com(self.l(env, flag), self.r(env, flag))

    def __repr__(self):
        l = repr(self.l)
        r = repr(self.r)
        if self.precedence > self.l.precedence:
            l = '(' + l + ')'
        if self.precedence > self.r.precedence:
            r = '(' + r + ')'
        return l + ' ' + self.symbol + ' ' + r


class UniOp(Base):
    ops = {'not': ('not ', op.not_, 3),
           '-': ('-', op.neg, 9)}
    def __init__(self, val, com):
        self.val = val
        self.symbol, self.com, self.precedence = self.ops[com.strip()]

    def __call__(self, env, flag=None):
        return self.com(self.val(env, flag))

    def __repr__(self):
        val = repr(self.val)
        if self.precedence > self.val.precedence:
            val = '(' + val + ')'
        return self.symbol + val
