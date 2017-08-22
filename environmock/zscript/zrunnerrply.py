from .rply.errors import *
from .zenv import Env
from .zlexerrply import lexer
from .zscriptrply import parser
from .zsyntaxtree import *


def printgen(gen):
    x = 0
    r = {}
    i = None
    z = next(gen)
    if type(z) != dict:
        if type(z) == complex:
            z = (z.real, z.imag)
        print(z)
        return z
    else:
        for var, val in z.items():
            r[var] = [val]
        for i in gen:
            x += 1
            [r[var].append(val) for var, val in i.items()]
            if x % 1 == 0:
                print(i)
        if i is not None:
            print(i)
    return r


def testparser(test):
    env = Env()
    plotting = []
    x = 0
    for instr in test.splitlines():
        tokens = lexer.lex(instr)
        try:
            pro = parser.parse(tokens)
        except LexingError as error:
            idx = error.source_pos.idx + 1
            raise SyntaxError('\n"{0}"\n'.format(instr)+(' '*idx)+'^'+'\nInvalid Symbol in line: %d, idx: %d' % (x, idx))
        except ParsingError as error:
            idx = error.source_pos.idx + 1
            raise SyntaxError('\n"{0}"\n'.format(instr)+(' '*idx)+'^'+'\nInvalid Syntax in line: %d, idx: %d' % (x, idx))
        try:
            out = pro(env)
        except Exception as error:
            raise Exception(error.message + '\nThere was an error while running the line: "%s" \nLineNo: %d' %(instr, x))
        if out is not None:
            try:
                plotting = printgen(out)
            except Exception as error:
                raise Exception(error.message + '\nThere was an error while running the line: "%s" \nLineNo: %d' %(instr, x))


        x += 1
    # showenv(env)
    return plotting


def compiler(instr, x=1):
    instr = instr.lower()
    tokens = lexer.lex(instr)
    try:
        tokens = list(tokens)
        if len(tokens) > 0:
            if tokens[0].gettokentype() == 'SPC':
                tokens.pop(0)
        if len(tokens) > 0:
            if tokens[-1].gettokentype() == 'SPC':
                tokens.pop(-1)

        def tokenizer(tokens):
            for t in tokens:
                yield t
        tokens = tokenizer(tokens)
    except LexingError as error:
        idx = error.source_pos.idx + 1
        raise SyntaxError(
            '\n"{0}"\n'.format(instr) + (' ' * idx) + '^' + '\nInvalid Symbol in line: %d, idx: %d' % (x, idx))
    try:
        tree = parser.parse(tokens)
    except ParsingError as error:
        idx = error.source_pos.idx + 1
        raise SyntaxError(
            '\n"{0}"\n'.format(instr) + (' ' * idx) + '^' + '\nInvalid Syntax in line: %d, idx: %d' % (x, idx))
    return tree


def runerror(e, instr, x):
    args = ', '.join([str(arg) for arg in e.args if type(arg) in (str,)])
    etype = e.__class__.__name__
    raise Exception(
        etype + ': ' + args + '\nThere was an error while running the line: "%s" \nLineNo: %d' % (instr, x))


def run(program, env, instr='', x=1):
    plotting = None
    try:
        out = program(env)
    except Exception as e:
        runerror(e, instr, x)
    if out is not None:
        try:
            plotting = printgen(out)
        except Exception as e:
            runerror(e, instr, x)
    return plotting


def compilerun(eq, env):
    x = 1
    nlines = eq.splitlines()
    lines = [line.split(';;')[0] for line in nlines]
    neq = [item for sublist in lines for item in sublist.split(';')]
    plottings = []
    for instr in neq:
        tree = compiler(instr, x)
        plot = run(tree, env, instr, x)
        if plot is not None:
            plottings.append(plot)
        x += 1
    return plottings


def repl(env=None):
    if env is None:
        env = Env(repl=True)
    eq = None
    print('Type in your Equation, "env" to see the variables, or "quit" to stop')
    while eq != 'quit':
        eq = input('>>> ')
        if eq == 'env':
            print(env)
        elif eq != 'quit':
            try:
                compilerun(eq, env)
            except Exception as message:
                print(message)
            for warning in ZWarning.currentwarnings:
                print(warning)
            ZWarning.clearwarnings()
    return env


if __name__ == '__main__':
    repl()
    consta = '''
        F = 1
        m = 1
        dt = 1
        p = 0
        p_ == p + dt*F
        v == p/m
        x = 0
        x_ == x + v_*dt
        trace v
        trace x
        next 10
        '''

    fib = '''
        t := 0
        dt := 1
        t_ = t + dt
        x := 1
        v := 1
        x_ = x + v
        v_ = x
        trace t
        trace v
        trace x
        next 20
        '''

    fib2 = '''
        t := 0
        ;;
        t
        dt = 1
        t_ = t + dt
        x := 2
        v := 1
        v_ = x + v
        x_ = x + v_
        v
        trace t
        trace v
        trace x
        next 10
        '''

    init_values = '''
         ballm := 0.402
         ballpx := 0.108
         ballpy := -0.763
         ballvx := 0.18
         ballvy := 0.0
         springx := -0.007
         springy := -0.0050

         t := 0
         dt := (1/210)/10
         g := -9.8
         ks := 6.83
         L0 := 0.123
         '''

    test_spring = '''
        Lmag = springy * 0.9
        Ly = ballpy - springy
        Lhy = Ly/Lmag
        s = Lmag-L0
        Fspringy = (-ks)*s*Ly
        ballpy
        springy
        Ly
        Fspringy
    '''

    spring = '''
        Lx = ballpx - springx
        Ly = ballpy - springy
        Lmag = (Lx^2 + Ly^2)^0.5
        Lhx = Lx/Lmag
        Lhy = Ly/Lmag
        s = Lmag - L0

        Fgravy = ballm*g

        Fspringx = -ks*s*Lhx
        Fspringy = -ks*s*Lhy

        Fnetx = Fspringx
        Fnety = Fspringy + Fgravy

        ballvx_ = ballvx + Fnetx/ballm*dt
        ballvy_ = ballvy + Fnety/ballm*dt

        ballpx_ = ballpx + ballvx_*dt
        ballpy_ = ballpy + ballvy_*dt

        t_ = t + dt
        t
        trace t
        trace ballpx
        trace ballpy
        trace Fnety
        trace Fspringy
        trace Lhy
        trace Ly
        next 11550
        '''

    # make this work - need comments and 'mag' function
    spring2 = '''
        ;;xh
        ;;yh
        ;; constant ;; values for this simulation
            ;;dt = (1/210)/10 ;;(1/210)
            ;;g = 9.8
            ;;ks = 6.83
            ;;L0 = 0.123
            g := g*yh
            Mball := ballm
            Xspring := springx*xh + springy*yh;; (springy+0.0002)*yh

        ;; initial values
            Xball := ballpx*xh + ballpy*yh
            Vball := ballvx*xh + ballvy*yh
            Vball := 50 * (xh + yh) ;; throw it super hard to start the weight/spring spinning around
            p := Vball*Mball
            ;;t = 0
            dLdt := 0
            Kfs := 0.1*2*(ks*Mball)^(1/2)  ;; optimal damping of spring
            Kfa := 0.01  ;; small air resistance

        ;; calculated values - current values, not 'next' values
            L = Xball - Xspring
            Lmag = mag L
            Lh = L/Lmag
            stretch = Lmag - L0
            Fs = -ks(stretch)Lh
            Ffs = -Kfs(dLdt)Lh ;; in the direction of the spring, against the spring movement
            Ffa = -Kfa*Vball ;; in the direction against velocity
            Fg = (Mball*g)
            Fnet = Fs + Fg + Ffs + Ffa
            Vball = p / Mball

        ;; next time step (create 'next' values)
            dLdt_ = (Lmag_ - Lmag)/dt  ;; differentiate length
            p_ = p + Fnet*dt  ;; momentum = integral of force
            Xball_ = Xball + Vball_*dt  ;; position = integral of velocity
            t_ = t + 1*dt  ;; Integrate time by a constant

        ;; run simulation
            trace t
            trace Xball
            trace dLdt
            next 50000
            '''

    spring3 = '''
            ;; constant ;; values for this simulation
                dt = (1/210)/10 ;;(1/210)
                ks := 6.83
                L0 := 0.123
                g := (0, -9.81)
                Mball := 0.402
                Xspring := (-0.007, -0.0050)

            ;; initial values
                Xball := (0.108, -0.763)
                Vball := (0.18, 0)*10
                ;;Vball := 50 * (1, 1) ;; throw it super hard to start the weight/spring spinning around
                p := Vball*Mball
                t := 0
                dLdt := 0
                Kfs := 0.1*2*(ks*Mball)^(1/2)  ;; optimal damping of spring
                Kfa := 0.01  ;; small air resistance

            ;; calculated values - current values, not 'next' values
                L = Xball - Xspring
                Lmag = mag L
                Lh = L/Lmag
                stretch = Lmag - L0
                Fs = -ks*stretch*Lh
                Ffs = -Kfs*dLdt*Lh ;; in the direction of the spring, against the spring movement
                Ffa = -Kfa*Vball ;; in the direction against velocity
                Fg = Mball*g
                Fnet = Fs + Fg + Ffs + Ffa
                Vball = p / Mball

            ;; next time step (create 'next' values)
                dLdt_ = (Lmag_ - Lmag)/dt  ;; differentiate length
                p_ = p + Fnet*dt  ;; momentum = integral of force
                Xball_ = Xball + Vball_*dt  ;; position = integral of velocity
                t_ = t + 1*dt  ;; Integrate time by a constant

            ;; run simulation
                trace t
                trace Xball
                trace dLdt
                next 23100
                graph Xball
                '''

    threebody = '''
        Xa := 1*xh + 1*yh
        Xb := 0-1*xh + 1*yh
        Xc := 0-1*yh
        Va := 0.01*yh
        Vb := (0-0.01)*yh
        Vc := 0
        Ma := 1*10^6
        Mb := 1*10^6
        Mc := 2*10^6
        Pa := Va*Ma
        Pb := Vb*Mb
        Pc := Vc*Mc
        Rab = Xb-Xa
        Rabmag = mag Rab
        Rabh = Rab/Rabmag
        Rbc = Xc-Xb
        Rbcmag = mag Rbc
        Rbch = Rbc/Rbcmag
        Rca = Xa-Xc
        Rcamag = mag Rca
        Rcah = Rca/Rcamag
        G := 6.67*10^(0-11)
        Fab = Rabh*Ma*Mb*G/Rabmag^2
        Fbc = Rbch*Mb*Mc*G/Rbcmag^2
        Fca = Rcah*Mc*Ma*G/Rcamag^2
        Fna = Fab - Fca
        Fnb = Fbc - Fab
        Fnc = Fca - Fbc
        Pa_ = Pa + Fna*dt
        Pb_ = Pb + Fnb*dt
        Pc_ = Pc + Fnc*dt
        Xa_ = Xa + Va_*dt
        Xb_ = Xb + Vb_*dt
        Xc_ = Xc + Vc_*dt
        Ka = Ma*(mag Va)^2/2
        Kb = Mb*(mag Vb)^2/2
        Kc = Mc*(mag Vc)^2/2
        Kt = Ka+Kb+Kc
        Va = Pa/Ma
        Vb = Pb/Mb
        Vc = Pc/Mc
        t := 0
        dt := 0.25 ;;0.5 ;; 1 or 0.5 split
        t_ = t + dt
        trace t
        trace Xa
        trace Xb
        trace Xc
        trace Kt
        next 27000
        '''

    climatechange = '''
        ts := 1
        dt := ts*365*24*60*60
        L := 1350
        albedo := 0.3
        epsilon := 1
        sigma := 5.67 * 10^(0-8)
        waterdepth := 400
        temp := 0
        t := 0
        heatcap := waterdepth * 4.2*1000^2
        heatcont := temp*heatcap
        in := L*(1-albedo)/4
        out = (temp^4)*sigma*epsilon

        heatcont_ = heatcont + (in-out)*dt
        temp_ = heatcont/heatcap
        t_ = t + ts
        trace t
        trace temp
        next 475

        '''

    stringtest = '''
        ;; sdkhfakdshf
        s := "hi my name is bob"
        s + s
        '''

    sqrt = '''
t := 0
t_ = t + 1
x := 1
sq := 101
sqrg = x^2
x_ = (x^2+sq)/(2*x)
trace t
trace x
trace sqrg
next 10
        '''

    # spring2 = init_values + spring2

    experiment = '''
            Fs = -ks(stretch)Lh
            Fks = -Kfs(dLdt)Lh ;; in the direction of the spring, against the spring movement
    '''

    booleantest = '''
    x := 2
    y := True
    x-or = x or y and not x and y
    x-or := 1
    c := 1
    -2x(c)x(c)3^c/x(c)x/(c)3(c)
    2x/3y
    '''

    # 2x/(x + 3)(x + 5)
    # 2x/(x + 3)(x + 5) * (x+7)
    # ((2x)/(x + 3))*(x + 5) * (x+7)
    # x / ((x + 3)*(x + 5))
    #
    # 3 / 4
    # 3/4
    # 3*x/(3*y)
    # 3x/3xy
    # 3x/(3x*y) /

    env1 = Env()
    out = compilerun(spring3, env1)
    with open('graph.html', 'w') as f:
        f.write(out[1])
    print(env1.object['data'])
    # print('done')
    # plottings = out
    # plotting = np.array(plottings[0])
    # plotting = plotting.T
    # # print(list(plotting))
    # # plt.plot(plotting[1], plotting[2])
    # plt.plot(plotting[1].real, plotting[1].imag)
    # # out = testparser(threebody)
    # plotting = np.array(out)
    # plotting = plotting.T
    # #print(plotting)
    # #plt.plot(plotting[1], plotting[2])
    # plt.plot(plotting[1].real, plotting[1].imag)
    # plt.plot(plotting[2].real, plotting[2].imag)
    # plt.plot(plotting[3].real, plotting[3].imag)
    # plt.scatter(-0.007, -0.0050)

    X = [-0.109, -0.08, -0.045, -0.004, 0.036, 0.071, 0.097, 0.108, 0.104, 0.088, 0.057, 0.019, -0.021, -0.062, -0.094,
         -0.115, -0.12, -0.113, -0.091, -0.06, -0.02, 0.023, 0.058, 0.089, 0.105, 0.107, 0.094, 0.068, 0.034, -0.008,
         -0.047, -0.084, -0.107, -0.121, -0.116, -0.098, -0.071, -0.034, 0.008, 0.048, 0.08, 0.101, 0.108, 0.1, 0.078,
         0.046, 0.007, -0.034, -0.07, -0.1, -0.116, -0.119, -0.106, -0.081, -0.045, -0.007, 0.036, 0.069, 0.096, 0.111,
         0.105, 0.086, 0.06, 0.022, -0.016, -0.057, -0.088, -0.113, -0.12, -0.113, -0.093, -0.061, -0.02, 0.022, 0.058,
         0.088, 0.105, 0.108, 0.096, 0.072, 0.037, -0.003, -0.042, -0.078, -0.104, -0.119, -0.118, -0.103, -0.074,
         -0.038, 0.004, 0.043, 0.078, 0.102, 0.11, 0.103]
    Y = [-0.643, -0.665, -0.686, -0.708, -0.732, -0.747, -0.759, -0.763, -0.754, -0.739, -0.719, -0.697, -0.678, -0.662,
         -0.651, -0.646, -0.654, -0.669, -0.689, -0.711, -0.731, -0.748, -0.758, -0.762, -0.754, -0.741, -0.722, -0.698,
         -0.678, -0.66, -0.651, -0.648, -0.655, -0.672, -0.688, -0.711, -0.729, -0.747, -0.759, -0.761, -0.753, -0.739,
         -0.718, -0.697, -0.676, -0.66, -0.652, -0.649, -0.654, -0.672, -0.688, -0.709, -0.731, -0.749, -0.757, -0.761,
         -0.754, -0.738, -0.719, -0.698, -0.678, -0.667, -0.655, -0.649, -0.655, -0.668, -0.687, -0.711, -0.732, -0.748,
         -0.754, -0.761, -0.757, -0.739, -0.719, -0.697, -0.68, -0.664, -0.655, -0.651, -0.659, -0.671, -0.69, -0.71,
         -0.729, -0.743, -0.756, -0.758, -0.75, -0.737, -0.718, -0.699, -0.677, -0.662, -0.654, -0.652]
    # plt.plot(X,Y)
    # plt.show()