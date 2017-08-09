
# coding: utf-8

# !/usr/bin/env python3

"""
Created on Mon Jan  7 13:14:00 2017

@author: zavidan
"""
from zlexer import lexer
##########
# Parser #
##########


class ParsingError(Exception):
    pass


def parser(terms):
    i, pro = program(terms)
    if i == len(terms):
        return pro
    else:
        raise ParsingError('Parsed Incorrectly')


def program(terms):
    terms = list(terms)
    i = 0
    exquations = []
    while i < len(terms):
        if terms[i][0] != 'NL':
            try:
                ni, exquation = resultbool(i, terms)
                if terms[ni][0] != 'NL':
                    raise ParsingError('End Parseing Too Soon')
            except ParsingError:
                try:
                    ni, exquation = setvar(i, terms)
                    if terms[ni][0] != 'NL':
                        raise ParsingError('End Parseing Too Soon')
                except ParsingError:
                    try:
                        ni, exquation = setfunction(i, terms)
                        if terms[ni][0] != 'NL':
                            raise ParsingError('End Parseing Too Soon')
                    except ParsingError:
                        ni, exquation = makelist(i, terms)

            i = ni
            exquations.append(exquation)

        if terms[i][0] == 'NL':
            i += 1
        else:
            s = ''
            for term in terms:
                if term[0] == 'NL':
                    break
                else:
                    s += term[1]

            raise ParsingError('Error in: ' + s)
    pro = Program(exquations)
    return i, pro


def setvar(i, terms):
    i, char = equals(i, terms)
    if terms[i][0] != 'LLB':
        i, explist = resultbool(i, terms)
    else:
        i, explist = makelist(i, terms)
    equation = Equation(char, explist)
    return i, equation


def setfunction(i, terms):
    i, char = same(i, terms)
    i, expression = resultbool(i, terms)
    function = Function(char, expression)
    return i, function


def resultbool(i, terms):
    i, arith1 = resultadd(i, terms)
    arith2 = None
    bol = None
    if terms[i][0] == 'COMP':
        bol = terms[i][1]
        i += 1
        if terms[i][0] == 'EQ':
            bol += terms[i][1]
        i, arith2 = resultadd(i, terms)
    boolean = Boolean(arith1, arith2, bol)
    return i, boolean


def resultadd(i, terms):
    factors = []
    addmins = []
    i, factor = resultmul(i, terms)
    factors.append(factor)
    while terms[i][0] == 'ADDMIN':
        addmin = terms[i][1]
        i += 1
        i, factor = resultmul(i, terms)
        addmins.append(addmin)
        factors.append(factor)
    expression = Expression(factors, addmins)
    return i, expression


def resultmul(i, terms):
    exponents = []
    muldivs = []
    i, exponent = resultexp(i, terms)
    exponents.append(exponent)
    while terms[i][0] == 'MULDIV':
        muldiv = terms[i][1]
        i += 1
        i, exponent = resultexp(i, terms)
        muldivs.append(muldiv)
        exponents.append(exponent)
    factor = Factor(exponents, muldivs)
    return i, factor


def resultexp(i, terms):
    exp = None
    i, base = operand(i, terms)
    if terms[i][0] == 'EXP':
        i += 1
        i, exp = operand(i, terms)
    exponent = Exponent(base, exp)
    return i, exponent


def makelist(i, terms):
    if terms[i][0] == 'LLB':
        i+=1
    else:
        raise ParsingError(terms[i][0]+ "!= 'LLB', Does not open List")

    vals = []
    i, val = resultbool(i, terms)
    vals.append(val)
    while terms[i][0] in ('SEP', 'LB', 'ADDMIN', 'CHAR', 'INT', 'FLOAT'):
        if terms[i][0] == 'SEP':
            i += 1
        i, val = resultbool(i, terms)
        vals.append(val)

    if terms[i][0] == 'LRB':
        i+=1
    else:
        raise ParsingError(terms[i][0] + "!= 'LLB', Does not close List")
    return i, List(vals)



def operand(i, terms):
    term = terms[i]
    addmin = '+'
    if term[0] == "ADDMIN":
        i += 1
        addmin = term[1]
        term = terms[i]

    if term[0] == 'INT':
        value = Int(term[1], addmin)

    elif term[0] == 'FLOAT':
        value = Float(term[1], addmin)

    elif term[0] == 'CHAR':
        value = Char(term[1], addmin)

    elif term[0] == 'LB':
        i += 1
        i, expression = resultbool(i, terms)
        if terms[i][0] == 'RB':
            value = Value(expression)
        else:
            raise ParsingError("{term} does not close expression, i = {i}".format(term=terms[i][0], i=i))

    else:
        raise ParsingError("{term} not in ( 'INT', 'FLOAT', 'CHAR' ) or {term} does not open an expression, i = {i}".format(term=term, i=i))
    return i+1, value


def equals(i, terms):
    eterm = terms[i+1][0]
    cterm = terms[i][0]

    if cterm == 'CHAR' and eterm == 'EQ':
        return i+2, terms[i][1]
    else:
        raise ParsingError("{a} != 'CHAR' and {b} != 'EQ, i = {i}'".format(a=cterm, b=eterm, i=i))


def same(i, terms):
    fterm = terms[i+1][0]
    cterm = terms[i][0]

    if cterm == 'CHAR' and fterm == 'FUNC':
        return i+2, terms[i][1]
    else:
        raise ParsingError("{a} != 'CHAR' or {b} != 'FUNC', i = {i}'".format(a=cterm, b=fterm, i=i))


###############
# Implementer #
###############


class RunError(Exception):
    pass


class ReturnValue:
    pass


class NotReturnValue:
    pass


class Program(NotReturnValue):
    def __init__(self, exquations):
        self.exquations = exquations

#         for exq in self.exquations:
#             if (type(exq) != Expression and type(exq) != Equation):
#                 raise ParsingError('self.exquations does not contain only types Equation and Expression: '+str(type(exq)))

    def __call__(self, env):
        for exq in self.exquations:
            result = exq(env)
            if result is not None:
                yield result


class Function(NotReturnValue):
    funcuse = {}

    def __init__(self, char, expression):
        self.char = char
        self.expression = expression


        used = self.varsused(self.expression)
        Function.funcuse[self.char] = used
        # Check For Circular References
        circle = self.circular(self.char)
        if circle:
            raise ParsingError('When defining the function: {a}, you created a circular reference.'.format(a=self.char))

    def circular(self, char):
        circle = False
        for var in self.funcuse[char]:
            if self.char == var:
                circle = True
            else:
                try:
                    circle = self.circular(var)
                except KeyError:
                    pass
            if circle:
                break
        return circle

    def varsused(self, expression):
        # returns all variables used in an expression
        used = []
        ariths = [expression.arith1]
        if expression.arith2 is not None:
            ariths.append(expression.arith2)
        for arith in ariths:
            for factor in arith.factors:
                for exponent in factor.exponents:
                    base = exponent.base.value
                    exp = exponent.exp
                    if type(base) is str:
                        used.append(base)
                    elif type(base) == Boolean:
                        used += self.varsused(base)

                    if exp is not None:
                        if type(exp.value) is str:
                            used.append(exp.value)
                        elif type(exp.value) == Boolean:
                            used += self.varsused(exp.value)
        return used

    def __call__(self, env):
        val = self.expression(env)
        #nextenv = dict(env)
        env[self.char] = self.expression


class Equation(NotReturnValue):
    def __init__(self, char, expression):
        self.char = char
        self.expression = expression

#         if type(self.expression) != Expression:
#             raise ParsingError('type(self.expression) is: '+str(type(self.expression)))

    def __call__(self, env):
        val = self.expression(env)
        env[self.char] = Value(val)


class Boolean(ReturnValue):
    def __init__(self, arith1, arith2=None, bol=None):
        self.arith1 = arith1
        self.arith2 = arith2
        self.bol = bol

    def __call__(self, env):
        result = self.arith1(env)
        if self.bol is not None:
            arith2 = self.arith2(env)
            if self.bol == '?=':
                result = result == arith2
            elif self.bol == '!=':
                result = result != arith2
            elif self.bol == '<':
                result = result < arith2
            elif self.bol == '<=':
                result = result <= arith2
            elif self.bol == '>':
                result = result > arith2
            elif self.bol == '>=':
                result = result >= arith2
        return result


class Expression(ReturnValue):
    def __init__(self, factors, addmins):
        self.addmins = addmins
        self.factors = factors

#         if len(self.addmins) != len(self.factors) - 1:
#             raise ParsingError("len(self.addmins)("+ str(len(self.addmins)) +") != len(self.factors)("+ str(len(self.factors)) +") - 1: ")
#         elif not('*' not in self.addmins and '/' not in self.addmins and '^' not in self.addmins):
#             raise ParsingError('self.addmins('+str(self.addmins)+') contains one of ["*", "/", "^"] ')
#         for factor in self.factors:
#             if type(factor) != Factor:
#                 raise ParsingError('self.factors does not contain only type Factor: '+str(factor))

    def __call__(self, env):
        result = self.factors[0](env)
        for factor, addmin in zip(self.factors[1:], self.addmins):
            value = factor(env)
            if addmin == '-':
                result -= value
            elif addmin == '+':
                result += value
        return result


class Factor(ReturnValue):
    def __init__(self, exponents, muldivs):
        self.exponents = exponents
        self.muldivs = muldivs

#         if len(self.muldivs) != len(self.exponents) - 1:
#             raise ParsingError("len(self.muldivs)("+ str(len(self.muldivs)) +") != len(self.exponents)("+ str(len(self.exponents)) +") - 1: ")
#         elif not('+' not in self.muldivs and '-' not in self.muldivs and '^' not in self.muldivs):
#             raise ParsingError('self.muldivs('+str(self.muldivs)+') contains one of ["+", "-", "^"] ')
#         elif sum([type(exp) == Exponent for exp in self.exponents]) != len(self.exponents):
#             raise ParsingError('self.exponents does not contain only type Exponent: '+str(self.exponents))

    def __call__(self, env):
        result = self.exponents[0](env)
        for exponent, muldiv in zip(self.exponents[1:], self.muldivs):
            value = exponent(env)
            if muldiv == '/':
                result /= float(value)
            elif muldiv == '*':
                result *= value
        return result


class Exponent(ReturnValue):
    def __init__(self, base, exp):
        self.base = base
        self.exp = exp

#         if type(self.base) != Value:
#             raise ParsingError('type(self.base) is: '+str(type(self.base)))
#         elif type(self.exp) != Value and self.exp is not None:
#             raise ParsingError('type(self.exp) is: '+str(type(self.exp)))

    def __call__(self, env):
        result = self.base(env)
        if self.exp is not None:
            result **= self.exp(env)
        return result


class Value(ReturnValue):
    def __init__(self, value, addmin='+'):
        self.value = value
        self.addmin = addmin

#         if type(self.value) != str and type(self.value) != Expression and type(self.value) != float and type(self.value) != int:
#             raise ParsingError('type(self.value) is: '+str(type(self.value)))

    def __call__(self, env):
        result = self.value
        if isinstance(self.value, Boolean):
            result = self.value(env)
        if type(result) is not bool:
            if self.addmin == '-':
                result = -result
            elif self.addmin == '+':
                result = result
        return result


class Int(Value):
    def __init__(self, value, addmin='+'):
        self.value = int(value)
        self.addmin = addmin


class Float(Value):
    def __init__(self, value, addmin='+'):
        self.value = float(value)
        self.addmin = addmin


class Char(Value):
    def __init__(self, value, addmin='+'):
        self.value = value
        self.addmin = addmin

    def __call__(self, env):
        try:
            result = env[self.value](env)
        except KeyError:
            raise RunError('The variable: ' + self.value + ' is not defined')
        if self.addmin == '-':
            result = -result
        elif self.addmin == '+':
            result = result
        return result


class List(Value):
    def __int__(self, value):
        self.value = value

    def __call__(self, env):
        result = []
        for val in self.value:
            result.append(val(env))
        return result


###################
# ZScript Runners #
###################

def newenv(): return {'True': Value(True), 'False': Value(False)}


def repl():
    env = newenv()
    Function.funcuse = {}
    eq = None
    print('Type in your Equation, "env" to see the variables, or "quit" to stop')
    while eq != 'quit':
        eq = input('>>> ')
        if eq == 'env':
            for k, v in env.items():
                print(k, ': ', v(env))
        elif eq != 'quit':
            try:
                output = list(compilerun(eq, env))
                if len(output) != 0:
                    print(output[0])
            except Exception as message:
                print(message)


def compilerun(eq, env):
    tree = compiler(eq)
    return run(tree, env)


def compiler(eq):
    terms = lexer(eq)
    terms.append(('NL', '\n'))

    parsetree = parser(terms)
    return parsetree


def run(tree, env):
    return tree(env)

