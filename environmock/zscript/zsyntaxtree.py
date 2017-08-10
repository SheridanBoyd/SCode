from collections import defaultdict
from rply.token import BaseBox


class ZWarning(Warning):
    currentwarnings = []
    def __init__(self, message):
        self.message = message
        self.currentwarnings.append(message)
        # showwarning(message, self.__class__(), '', '', line='')

    @classmethod
    def clearwarnings(cls):
        cls.currentwarnings = []


class Base(BaseBox):
    def __call__(self, env, flag=None):
        pass

    def __repr__(self):
        return ''

    def _pyrepr(self):
        return 'Base()'


class NOP(Base):
    def __repr__(self):
        return ''

    def _pyrepr(self):
        return 'NOP()'


class Print(Base):
    def __init__(self, eq):
        self.eq = eq

    def __call__(self, env, flag=None):
        yield self.eq(env, flag)

    def __repr__(self):
        return repr(self.eq)

    def _pyrepr(self):
        return 'Print({0})'.format(self.eq._pyrepr())


class Value(Base):
    def __init__(self, value, posmin):
        self.value = value
        self.posmin = posmin

    def __call__(self, env, flag=None):
        if self.posmin == '-':
            r = - self.value(env, flag)
        else:
            r = + self.value(env, flag)
        return r

    def __repr__(self):
        return self.posmin + repr(self.value)

    def _pyrepr(self):
        return 'Value({0}, "{1}")'.format(self.value._pyrepr(), self.posmin)


class Literal(Base):
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

    def _pyrepr(self):
        if type(self.val) == str:
            return 'Literal("{0}")'.format(self.val)
        else:
            return 'Literal({0})'.format(self.val)


class String(Literal):
    def __init__(self, val):
        assert type(val) == str
        Literal.__init__(self, val)

    def __repr__(self):
        return '"{0}"'.format(self.val)

    def _pyrepr(self):
        return 'String({0})'.format(self.val)


class Number(Literal):
    def __init__(self, val):
        assert type(val) == float
        Literal.__init__(self, val)

    def __repr__(self):
        return str(self.val)

    def _pyrepr(self):
        return 'Number({0})'.format(self.val)


class Boolean(Literal):
    def __init__(self, val):
        assert type(val) == bool
        Literal.__init__(self, val)

    def __repr__(self):
        return str(self.val)

    def _pyrepr(self):
        return 'Boolean({0})'.format(self.val)


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

    def _pyrepr(self):
        return 'Vector({0}, {1})'.format(self.x, self.y)


class Variable(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env, flag=None):
        if flag is not None:
            return env[self.var, flag]
        else:
            return env[self.var, 'cur']

    def __repr__(self):
        return self.var

    def _pyrepr(self):
        return 'Variable("{0}")'.format(self.var)


class SetVar(Base):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def __call__(self, env, flag=None):
        env[self.var, 'val'] = Literal(self.val(env, 'nxt'))

    def __repr__(self):
        return self.var + ' := ' + repr(self.val)

    def _pyrepr(self):
        return 'SetVar("{0}", {1})'.format(self.var, self.val._pyrepr())


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

    def _pyrepr(self):
        return 'SetDef("{0}", {1}, {2})'.format(self.var, self.func._pyrepr(), self.cur)


class Function(Base):
    def __init__(self, func, inpt):
        self.func = func
        self.inpt = inpt

    def __call__(self, env, flag=None):
        function = env[self.func, 'func']
        return function(self.inpt, flag)

    def __repr__(self):
        return self.func + ' ' + repr(self.inpt)

    def _pyrepr(self):
        return 'Function("{0}", {1})'.format(self.func, self.inpt._pyrepr())


class Next(Base):
    def __init__(self, loops):
        self.loops = loops

    def __call__(self, env, flag=None):
        tenv = env.object['trc']
        nenv = env.object['nxt']
        c = [env[var, 'cur'] for var in tenv]
        yield c
        for i in xrange(self.loops):
            newvalues = env.object['val'].copy()
            for var, eq in nenv.items():
                try:
                    v = Literal(eq(env, flag))
                except Exception as e:
                    message = e.message
                    args = str(e.args)[1:-1]
                    error = e.__class__()
                    error.message = args+message+'\nThere was an error while updating "%s"\n%s_ = %s' % (var, var, eq)

                    raise error
                newvalues[var] = v
            env.object['val'] = newvalues
            c = [env[var, 'cur'] for var in tenv]
            #print(c)
            yield c

    def __repr__(self):
        return 'next ' + str(self.loops)

    def _pyrepr(self):
        return 'Next({0})'.format(self.loops)


class NextVariable(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env, flag=None):
        return env[self.var, 'nxt']

    def __repr__(self):
        return self.var + '_'

    def _pyrepr(self):
        return 'NextVariable("{0}")'.format(self.var)


class Trace(Base):
    def __init__(self, var):
        self.var = var

    def __call__(self, env, flag=None):
        env.object['trc'].append(self.var)

    def __repr__(self):
        return 'trace ' + self.var

    def _pyrepr(self):
        return 'Trace("{0}")'.format(self.var)


class BinOp(Base):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def _pyrepr(self):
        return 'BinOp({0}, {1})'.format(self.l._pyrepr(), self.r._pyrepr())


class Compare(Base):
    def __init__(self, l, r, com):
        if '==' in com:
            self.com = ET(l, r)
        elif '!=' in com:
            self.com = NET(l, r)
        elif '>=' in com:
            self.com = MTOET(l, r)
        elif '<=' in com:
            self.com = LTOET(l, r)
        elif '>' in com:
            self.com = MT(l, r)
        elif '<' in com:
            self.com = LT(l, r)

    def __call__(self, env, flag=None):
        return self.com(env, flag)

    def __repr__(self):
        return repr(self.com)


class ET(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) == self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' == ' + repr(self.r)


class NET(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) != self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' != ' + repr(self.r)


class MTOET(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) >= self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' >= ' + repr(self.r)


class LTOET(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) <= self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' <= ' + repr(self.r)


class MT(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) > self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' > ' + repr(self.r)


class LT(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) < self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' < ' + repr(self.r)


class And(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) and self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' and ' + repr(self.r)


class Or(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) or self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' or ' + repr(self.r)


class Not(Base):
    def __init__(self, bool):
        self.bool = bool

    def __call__(self, env, flag=None):
        return not self.bool(env, flag)

    def __repr__(self):
        return 'not ' + repr(self.bool)


class Add(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) + self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' + ' + repr(self.r)

    def _pyrepr(self):
        return 'Add({0}, {1})'.format(self.l._pyrepr(), self.r._pyrepr())


class Sub(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) - self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' - ' + repr(self.r)

    def _pyrepr(self):
        return 'Sub({0}, {1})'.format(self.l._pyrepr(), self.r._pyrepr())


class Mul(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) * self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' * ' + repr(self.r)

    def _pyrepr(self):
        return 'Mul({0}, {1})'.format(self.l._pyrepr(), self.r._pyrepr())


class Div(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) / self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + ' / ' + repr(self.r)

    def _pyrepr(self):
        return 'Div({0}, {1})'.format(self.l._pyrepr(), self.r._pyrepr())


class Exp(BinOp):
    def __call__(self, env, flag=None):
        return self.l(env, flag) ** self.r(env, flag)

    def __repr__(self):
        return repr(self.l) + '^' + repr(self.r)

    def _pyrepr(self):
        return 'Add({0}, {1})'.format(self.l._pyrepr(), self.r._pyrepr())


class EnvGetValExt:
    def __init__(self, parent, flag):
        self.flag = flag
        self.parent = parent

    def __getitem__(self, item):
        return self.parent.__getitem__(item, self.flag)


class EnvGetObjExt:
    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, flag):
        return self.parent.getobject(flag)

    def __setitem__(self, flag, value):
        if flag == 'val':
            self.parent.value = value
        else:
            raise Exception('Cannot change any thing other than the val library')


class FuncCall:
    def __init__(self, func):
        self.func = func

    def __call__(self, env):
        def call(inpt, flag):
            return self.func(inpt(env, flag))
        return call

    def __repr__(self):
        return 'FuncCall({0}, "{0}")'.format(self.func.__name__)


class Env:
    defvalue = lambda x: {}
    defnextval = lambda x: {}
    defcurrent = lambda x: {'xh': Number(1.0), 'yh': Literal(1j), 'True': Boolean(True), 'False': Boolean(False)}
    deftrace = lambda x: []
    defdefdepent = lambda x: defaultdict(list)
    deffunctions = lambda x: {'mag': FuncCall(abs)}

    def __init__(self, repl=False, value=False, nextval=False, current=False, defdepent=False, trace=False, functions=False):
        self.repl = repl
        if not value: self.value = self.defvalue()
        else: self.value = value
        if not nextval: self.nextval = self.defnextval()
        else: self.nextval = nextval
        if not nextval: self.current = self.defcurrent()
        else: self.current = current
        if not defdepent: self.defdepent = self.defdefdepent()
        else: self.defdepent = defdepent
        if not trace: self.trace = self.deftrace()
        else: self.trace = trace
        if not functions: self.functions = self.deffunctions()
        else: self.functions = functions
        self.object = EnvGetObjExt(self)

    def __getitem__(self, itemflag):
        item = itemflag[0]
        flag = itemflag[1]
        if flag == 'func' and item in self.functions:
            return self.functions[item](self)
        elif flag == 'nxt' and item in self.nextval:
            return self.nextval[item](self, None)
        elif (flag == 'nxt' or flag == 'cur') and item in self.current:
            return self.current[item](self, flag)
        elif (flag == 'nxt' or flag == 'cur') and item in self.value:
            return self.value[item](self, flag)
        else:
            if flag == 'nxt' or flag == 'cur' or flag == 'func':
                if flag == 'cur' and item in self.nextval:
                    raise NameError('The definition "%s" needs to be initalized first' % item)
                else:
                    raise NameError("I can't find the value corresponding to %s" % item)
            else:
                raise Exception('The flag "%s" is not a valid flag' % flag)

    def __setitem__(self, itemflag, value):
        item = itemflag[0]
        flag = itemflag[1]
        if flag == 'nxt' or flag == 'cur':
            if (item in self.current or item in self.nextval):  # Checks for Re-Definition of Next/Current Definitions
                if not (self.repl):
                    raise Exception('Cannot Redefine The Definition "%s"' % item)
                else:
                     ZWarning('You are changing a variable Definition. If you wish to change this regularly use :=')
            circle, future = self.circleref(item, value, flag)
            if circle:  # Checks for Circular Referencing
                raise Exception('Circular Reference found when defining "%s"' % item)
            elif flag == 'nxt':
                if self.repl and (item in self.current):
                    del self.current[item]
                self.nextval[item] = value
            elif flag == 'cur':
                if future:  # Checks for Future Definitions in Current Definitions
                    raise SyntaxError('Trying to reference a Future Definition in "%s"' % item)
                else:
                    if item in self.value:  # Deletes Old Value copy of New Current Definition
                        del self.value[item]
                    if item in self.nextval:
                        del self.nextval[item]
                    self.current[item] = value
        elif flag == 'val':
            if not(self.repl) and (item in self.current):  # Checks for a Current Definition by the same Identifier
                raise Exception("Can't change a Current Definition to a Variable '%s'" % item)
            else:
                if self.repl and (item in self.current):
                    del self.current[item]
                self.value[item] = value
        else:
            raise Exception('The flag "%s" is not a valid flag' % flag)

    def getobject(self, flag):
        if flag == 'nxt':
            return self.nextval
        elif flag == 'cur':
            return self.current
        elif flag == 'val':
            return self.value
        elif flag == 'trc':
            return self.trace
        elif flag == 'func':
            return self.functions
        else:
            raise Exception('The flag "%s" is not a valid flag' % flag)

    def circleref(self, ident, prgr, flag):
        """ident: a String of the Definition Identifier
        prgr: an Object that contains the Definition Program

        Returns: a Tuple of Booleans
        First Bool tells if there is circle reference
        Second Bool tells if it references a future definition
        Example: (True, False)"""

        test = TestEnv()
        if flag == 'nxt':
            ident += '_'
        prgr(test)
        future = len(test.object['nxt']) != 0
        self.defdepent[ident] = list(test.object['nxt'].keys()) + list(test.object['cur'].keys())

        def findfuncs(dependent, ident, var):
            funcs = dependent[var]
            if ident in funcs:
                return True
            else:
                for func in funcs:
                    return findfuncs(dependent, ident, func)
        circle = findfuncs(self.defdepent, ident, ident)
        ident = ident[:-1]
        return circle, future

    def __pyrepr__(self):
        edit = self.defdepent.__repr__()
        reprdefdepent = edit[:12] + edit[19:23] + edit[25:]

        return 'Env({0}, {1}, {2}, {3}, {4}, {5})'.format(self.value.__repr__(),
                                                               self.current.__repr__(),
                                                               self.nextval.__repr__(),
                                                               reprdefdepent,
                                                               self.trace.__repr__(),
                                                               self.functions.__repr__())

    def __repr__(self):
        current = self.current.copy()
        del current['xh']
        del current['yh']
        del current['True']
        del current['False']
        program = ''

        value = '\n'.join([repr(SetVar(var, val)) for var, val in self.value.items()])
        if value:
            program += value + '\n'

        current = '\n'.join([repr(SetDef(var, val, True)) for var, val in current.items()])
        if current:
            program += current + '\n'

        nextval = '\n'.join([repr(SetDef(var, val, False)) for var, val in self.nextval.items()])
        if nextval:
            program += nextval + '\n'

        for var in self.trace:
            program += repr(Trace(var)) + '\n'

        return program


class TestEnv(Env):
    def __init__(self):
        def z(): return Literal(1)
        def func(env):
            def testcall():
                def thing2(inpt, flag):
                    return inpt(env)
                return thing2
            return testcall
        self.value = defaultdict(z)
        self.nextval = defaultdict(z)
        self.current = defaultdict(z)
        self.functions = defaultdict(func(self))
        self.object = EnvGetObjExt(self)

    def __getitem__(self, itemflag):
        item = itemflag[0]
        flag = itemflag[1]
        if flag == 'func':
            return self.functions[item]
        elif flag == 'nxt':
            return self.nextval[item+'_'](self, flag)
        elif flag == 'cur':
            return self.current[item](self, flag)
        else:
            raise Exception('The flag "%s" is not a valid flag' % flag)

if __name__ == '__main__':
    e = Env()
    b = TestEnv().current
    print(b)
    a = Function('mag', Literal(1 + 1j))
    print(a(e))
    print(e.nextval)
    env = Env({'False': Boolean(False), 'sq': Literal(101.0), 'True': Boolean(True), 't': Literal(10.0),
         'x': Literal(10.0498756211)}, {'yh': Literal(1j), 'xh': Number(1.0), 'sqrg': Exp(Variable("x"), Number(2.0))},
        {'x': Div(Add(Exp(Variable("x"), Number(2.0)), Variable("sq")), Mul(Number(2.0), Variable("x"))),
         't': Add(Variable("t"), Number(1.0))},
        defaultdict(list, {'t_': ['t'], 'x': [], 'x_': ['x', 'sq'], 't': [], 'sqrg': ['x']}), ['t', 'x', 'sqrg'],
        {'mag': FuncCall(abs)})

