class Endline(object):
    def __init__(self):
        pass

    def __str__(self):
        return '\n'

    def __repr__(self):
        return '\n'

    def htmlstr(self, environment):
        return '<br>'


class Chars(object):
    def __init__(self, characters):
        self.characters = characters

    def getCharacters(self):
        return self.characters

    def __str__(self):
        return self.characters

    def __repr__(self):
        return self.characters

    def htmlstr(self, environment):
        return self.characters


class Room_desc(object):
    def __init__(self, itemlist):
        self.itemlist = itemlist

    def getItemList(self):
        return self.itemlist

    def __str__(self):
        return''.join([str(i) for i in self.itemlist])

    def __repr__(self):
        return ''.join([repr(i) for i in self.itemlist])

    def htmlstr(self, environment):
        return ''.join([i.htmlstr(environment) for i in self.itemlist])


class Room(object):
    def __init__(self, name, room_desc):
        self.name = name
        self.room_desc = room_desc
        self.links = []
        for i in room_desc.itemlist:
            if type(i) == Link:
                self.links.append(repr(i.linkto))
        print(self.links)

    def __str__(self):
        return '#%s\n%s' % (str(self.name), str(self.room_desc))

    def __repr__(self):
        return '#%s\n%s' % (repr(self.name), repr(self.room_desc))

    def htmlstr(self, environment):
        return '''<h1>%s</h1><br>%s''' % (self.name.htmlstr(environment), self.room_desc.htmlstr(environment))


class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def getName(self):
        return self.name

    def __str__(self):
        return ('\n object name:' + str(self.name) + ' Object description' + str(self.description))

    def __repr__(self):
        return '##%s\n%s' % (repr(self.name), repr(self.description))


class Text_Adventure(object):
    def __init__(self, itemlist):
        self.itemlist = itemlist
        self.rooms = {}
        self.items = {}
        for room in itemlist:
            if type(room) == Room:
                self.rooms[room[0].name] = room
        print(self.rooms)

    def getItemList(self):
        return self.itemlist

    def __str__(self):
        return '\n\n'.join([str(i) for i in self.itemlist[0]]) + '\n\n'

    def __repr__(self):
        return '\n\n'.join([repr(i) for i in self.itemlist]) + '\n\n'

    def htmlstr(self, environment):
        htmldict = {}
        for thing in self.itemlist:
            htmldict[repr(thing.name)] = thing.htmlstr(environment)
        return htmldict


class Link(object):
    def __init__(self, linkto, alttext=None):
        self.linkto = linkto
        self.alttext = alttext

    def __str__(self):
        if self.alttext == None:
            return '[[%s]]' % (str(self.linkto))
        else:
            return '[[%s|%s]]' % (str(self.linkto), str(self.alttext))


    def __repr__(self):
        if self.alttext == None:
            return '[[%s]]' % (repr(self.linkto))
        else:
            return '[[%s|%s]]' % (repr(self.linkto), repr(self.alttext))

    def htmlstr(self, environment):
        if self.alttext == None:
            return '<a href="/%s/rooms/%s">%s</a>' % (
            environment['token'], self.linkto.htmlstr(environment), self.linkto.htmlstr(environment))
        else:
            return '<a href="/%s/rooms/%s">%s</a>' % (
            environment['token'], self.linkto.htmlstr(environment), self.alttext.htmlstr(environment))


class Special(object):
    def __init__(self, conditions, guard_desc):
        self.conditions = conditions
        self.guard_desc = guard_desc

    def __str__(self):
        return '@%s/%s/' % (str(self.conditions), str(self.guard_desc))

    def __repr__(self):
        return '@%s/%s/' % (repr(self.conditions), repr(self.guard_desc))

    def htmlstr(self, environment):
        if list(zs.compilerun(repr(self.conditions), environment['zenvironment']))[0]:
            return '<br>' + str(self.guard_desc.htmlstr(environment))
        else:
            return ''  # list(zs.compilerun(repr(self.conditions),environment['zenvironment']))[0]


class ItemInRoom(object):
    def __init__(self):
        pass


class Player(object):
    def __init__(self, inventory=[], room='start'):
        self.inventory = inventory
        self.room = room

    def __call__(self, textadventure):
        inputed = ''
        while inputed != 'quit':
            print(repr(textadventure.rooms[self.room]))
            for link in textadventure.rooms[self.room].links:
                print('you can go to ' + link)
            inputed = input('>>')
            if inputed in textadventure.rooms[self.room].links:
                self.room = inputed
            else:
                print("I'm sorry, you can not go there")


class Script(object):
    def __init__(self, script):
        self.script = script

    def __str__(self):
        return '{' + str(self.script) + '}'

    def htmlstr(self, environment):
        zlist = list(zs.compilerun(repr(self.script), environment['zenvironment']))
        strzlist = []
        [strzlist.append(str(i)) for i in zlist]
        return ''.join(strzlist)


class Exit(object):
    def __init__(self, enters):
        self.enters = enters

    def htmlstr(self, environment):
        return '<br><br>'
