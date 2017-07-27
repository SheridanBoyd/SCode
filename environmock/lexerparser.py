#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 12:05:32 2017

@author: zavidan
"""

import zscript as zs

# Defining the exceptions ##############################################################################################
class LexingError(Exception):
    pass

class ParsingError(Exception):
    pass

# Defining the helper functions for the lexer ##########################################################################
# This function accepts normal character and returns how many there are
def numChars(i,textlist):
    numchars = -1
    valid = [' ','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0','?','\'','!','’','.',',','#','-','_','\\','"','=','/',':','~','&','$','^','*','(',')','+',';']
    true = textlist[i] in valid
    while true:
        numchars += 1
        i += 1
        try:
            true = textlist[i] in valid
        except:
            true = False
    return numchars

# This function accepts '\n' , which is a new line, for the lexer
def exit(i,textlist):
    numreturns = -1
    loop = 1
    while loop == 1:
        try:
            if textlist[i] == '\n':
                numreturns += 1
                i += 1
            else:
                loop = 0
        except:
            loop = 0
    return numreturns

# This function accepts '\r' , which is also a new line, for the lexer
def rexit(i,textlist):
    numreturns = -1
    loop = 1
    while loop == 1:
        try:
            if textlist[i] == '\r':
                numreturns += 1
                i += 1
            else:
                loop = 0
        except:
            loop = 0
    return numreturns

# This function accepts '\r\n' , which is also a new line, for the lexer
def rnexit(i,textlist):
    numreturns = -1
    loop = 1
    while loop == 1:
        try:
            if textlist[i] == '\r' and textlist[i+1] == '\n':
                numreturns += 2
                i += 2
            else:
                loop = 0
        except:
            loop = 0
    return numreturns

# This function counts the number of #'s for the lexer
def oor(i,textlist): #oor means Object or Room
    numhash = 0
    while textlist[i] == '#':
        numhash += 1
        i += 1
    return numhash

# Defining the lexer ###################################################################################################
def lex(text):
    text = text + '\n\n\n\n'
    textlist = list(text)
    tokenlist = []
    i = 0
    while i <= (len(text) -1):
        if textlist[i] == '#':
            if textlist[i+1] == '#':
                tokenlist.append(('NEW_OBJECT','##'))
                i += 1
            else:
                tokenlist.append(('NEW_ROOM','#'))
        elif textlist[i] == '[':
            if textlist[i+1] == '[':
                tokenlist.append(('OPEN_LINK','[['))
                i += 1
            else:
                raise LexingError(textlist[i],i)
        elif textlist[i] == ']':
            if textlist[i+1] == ']':
                tokenlist.append(('CLOSE_LINK',']]'))
                i += 1
            else:
                raise LexingError(textlist[i],i)
        elif textlist[i] == '{':
            tokenlist.append(('OPEN_SCRIPT','{'))
        elif textlist[i] == '}':
            tokenlist.append(('CLOSE_SCRIPT','}'))

        elif textlist[i] == '\r':
            if textlist[i+1] == '\n':
                numreturns = rnexit(i, textlist)
                if numreturns == 1:
                    tokenlist.append(('END_LINE', '\r\n'))
                else:
                    tokenlist.append(('EXIT', '\r\n' * ((numreturns + 1)/2)))
                i += numreturns
            else:
                numreturns = rexit(i, textlist)
                if numreturns == 0:
                    tokenlist.append(('END_LINE', '\r'))
                else:
                    tokenlist.append(('EXIT', '\r' * (numreturns + 1)))
                    i += numreturns
        elif textlist[i] == '\n':
            numreturns = exit(i,textlist)
            if numreturns == 0:
                tokenlist.append(('END_LINE','\n'))
            else:
                tokenlist.append(('EXIT','\n'*(numreturns+1)))
                i += numreturns
        elif textlist[i] == '|':
            tokenlist.append(('ALT_TEXT','|'))
        elif textlist[i] == '@':
            tokenlist.append(('NEW_GUARD','@'))
        elif textlist[i] == '`':
            tokenlist.append(('GUARD_LIMIT','`'))
        else:
            tempi = i
            thing = numChars(i,textlist)
            if thing > -1:
                i += thing
                tokenlist.append(('CHARS',''.join(textlist[tempi:i+1])))
            else:
                raise LexingError(textlist[i],i)
        
        i += 1
    return tokenlist


# Defining the objects for parsing #####################################################################################
class Endline(object):
    def __init__(self):
        pass
    
    def __str__(self):
        return 'END_LINE'
    
    def __repr__(self):
        return '\n'
    
    def htmlstr(self,environment):
        return '<br>'
    
class Chars(object):
    def __init__(self,characters):
        self.characters = characters
        
    def getCharacters(self):
        return self.characters
    
    def __str__(self):
        return('\n chars:'+str(self.characters))
    
    def __repr__(self):
        return self.characters
    
    def htmlstr(self,environment):
        return self.characters
    
class Room_desc(object):
    def __init__(self,itemlist):
        self.itemlist = itemlist
        
    def getItemList(self):
        return self.itemlist
    
    def __str__(self):
        itemstr = []
        for i in self.itemlist:
            itemstr.append('\n room_desc item:'+str(i))
        return ''.join(itemstr)
    
    def __repr__(self):
        return ''.join([repr(i) for i in self.itemlist])
    
    def htmlstr(self,environment):
        return ''.join([i.htmlstr(environment) for i in self.itemlist])
    
                                 
class Room(object):
    def __init__(self,name,room_desc):
        self.name = name
        self.room_desc = room_desc
        self.links = []
        for i in room_desc.itemlist:
            if type(i) == Link:
                self.links.append(repr(i.linkto))
        print(self.links)
    
    def getName(self):
        return self.name
    
    def getRoom_desc(self):
        return self.room_desc
    
    def __str__(self):
        return('\n room name:' + str(self.name)+', room description:' + str(self.room_desc))
    
    def __repr__(self):
        return '#%s\n%s' %(repr(self.name),repr(self.room_desc))
    
    def htmlstr(self,environment):
        return '''<h1>%s</h1><br>%s''' % (self.name.htmlstr(environment),self.room_desc.htmlstr(environment))
    

class Item(object):
    def __init__(self,name,description):
        self.name = name
        self.description = description
        
    def getName(self):
        return self.name
    
    def __str__(self):
        return('\n object name:' + str(self.name) + ' Object description' + str(self.description))
    
    def __repr__(self):
        return '##%s\n%s' % (repr(self.name),repr(self.description))
        
class Text_Adventure(object):
    def __init__(self,itemlist):
        self.itemlist = itemlist
        self.rooms = {}
        self.items = {}
        for thing in itemlist:
            if type(thing) == Room:
                self.rooms[repr(thing.name)] = thing
            else:
                self.items[repr(thing.name)] = thing
        print(self.rooms)
        
    def getItemList(self):
        return self.itemlist
    
    def __str__(self):
        itemstr = []
        num = 0
        for i in self.itemlist:
            num += 1
            print(str(num)+str(i))
#             itemstr.append(str(num)+str(i))
        return ''
    
    def __repr__(self):
        return '\n\n'.join([repr(i) for i in self.itemlist]) + '\n\n'
        
    def htmlstr(self,environment):
        htmldict = {}
        for thing in self.itemlist:
            htmldict[repr(thing.name)] = thing.htmlstr(environment)
        return htmldict

class Link(object):
    def __init__(self,linkto,alttext=None):
        self.linkto = linkto
        self.alttext = alttext
        
    def __str__(self):
        if self.alttext == None:
            return 'links to:'+str(self.linkto)
        else:
            return 'links to:'+str(self.linkto)+' alt text:'+str(self.alttext)
        
    def __repr__(self):
        if self.alttext == None:
            return '[[%s]]' %(repr(self.linkto))
        else:
            return '[[%s|%s]]' %(repr(self.linkto),repr(self.alttext))
        
    def htmlstr(self,environment):
        if self.alttext == None:
            return '<a href="/%s/rooms/%s">%s</a>' %(environment['token'],self.linkto.htmlstr(environment),self.linkto.htmlstr(environment))
        else:
            return '<a href="/%s/rooms/%s">%s</a>' %(environment['token'],self.linkto.htmlstr(environment),self.alttext.htmlstr(environment))
        
class Guard(object):
    def __init__(self,conditions,guard_desc):
        self.conditions = conditions
        self.guard_desc = guard_desc
        
    def  __str__(self):
        return 'conditions:%s guard_desc: %s' % (str(self.conditions),str(self.guard_desc))
        
    def __repr__(self):
        return '@%s/%s/' % (repr(self.conditions),repr(self.guard_desc))

    def htmlstr(self,environment):
        if list(zs.compilerun(repr(self.conditions),environment['zenvironment']))[0]:
            return '\n' + str(self.guard_desc.htmlstr(environment))
        else:
            return ''#list(zs.compilerun(repr(self.conditions),environment['zenvironment']))[0]
    
class ItemInRoom(object):
    def __init__(self):
        pass
    
class Player(object):
    def __init__(self,inventory = [], room = 'start'):
        self.inventory = inventory
        self.room = room
        
    def __call__(self,textadventure):
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

class Variable(object):
    def __init__(self,script):
        self.script = script

    def htmlstr(self,environment):
        zlist = list(zs.compilerun(repr(self.script), environment['zenvironment']))
        strzlist =[]
        [strzlist.append(str(i)) for i in zlist]
        return ''.join(strzlist)

class Exit(object):
    def __init__(self,enters):
        self.enters = enters

    def htmlstr(self, environment):
        return '<br><br>'


# Defining the parser ##################################################################################################
def parser(lexedstring):
    return text_adventure(0, lexedstring)

def text_adventure(i,lexedstring):
    itemlist = []
    while i < len(lexedstring):
        try:
            nexti, newroom = room(i,lexedstring)
            itemlist.append(newroom)
        except ParsingError:
            nexti,newitem = item(i,lexedstring)
            itemlist.append(newitem)
        i = nexti
        try:
            if lexedstring[i][0] != 'EXIT':
                raise ParsingError('Does not EXIT', i, lexedstring[i])
            else:
                i += 1
        except IndexError:
            raise ParsingError('Needs an extra enter/return at the end of the file')
    return Text_Adventure(itemlist)
    
def room(i,lexedstring):
    if lexedstring[i][0] == 'NEW_ROOM' and lexedstring[i+1][0] == 'CHARS' and lexedstring[i+2][0] == 'END_LINE':
        name = lexedstring[i+1][1]
        i += 3
        i,itemlist = room_desc(i,lexedstring)
        return i,Room(Chars(name),itemlist)
    else:
        raise ParsingError('Does not contain the proper fromat for a room')
              
def room_desc(i,lexedstring):
    valid = ['CHARS','END_LINE','OPEN_OBJECT','CLOSE_OBJECT','EXIT']
    itemlist = []
    while i < len(lexedstring):
        if lexedstring[i][0] == 'EXIT' :
            try:
                if lexedstring[i + 1][0] == 'NEW_ROOM':
                    break
            except:
                break
        if lexedstring[i][0] == 'GUARD_LIMIT':
            break
        if lexedstring[i][0] in valid:
            if lexedstring[i][0] == 'CHARS':
                itemlist.append(Chars(lexedstring[i][1]))
            elif lexedstring[i][0] == 'END_LINE':
                itemlist.append(Endline())
            elif lexedstring[i][0] == 'EXIT':
                itemlist.append(Exit(lexedstring[i][1]))
            i += 1
        else:
            try:
                i,newlink = link(i,lexedstring)
                itemlist.append(newlink)
            except ParsingError:
                try:
                    i,newguard = guard(i,lexedstring)
                    itemlist.append(newguard)
                    i +=1
                except ParsingError:
                    try:
                        i,newscript = variable(i,lexedstring)
                        itemlist.append(newscript)
                    except ParsingError:
                        raise ParsingError('OH NOES THE ROOM DESCRIPTION IS INVALID')

    return i,Room_desc(itemlist)

def link(i,lexedstring):
    if lexedstring[i][0] == 'OPEN_LINK' and lexedstring[i+1][0] == 'CHARS' and lexedstring[i+2][0] == 'CLOSE_LINK':
        return i+3,Link(Chars(lexedstring[i+1][1]))
    elif lexedstring[i][0] == 'OPEN_LINK' and lexedstring[i+1][0] == 'CHARS' and lexedstring[i+2][0] == 'ALT_TEXT' and lexedstring[i+3][0] == 'CHARS' and lexedstring[i+4][0] == 'CLOSE_LINK':
        return i+5,Link(Chars(lexedstring[i+1][1]),Chars(lexedstring[i+3][1]))
    else:
        raise ParsingError('not a link')
    
def item(i,lexedstring):
    if lexedstring[i][0] == 'NEW_OBJECT' and lexedstring[i+1][0] == 'CHARS' and lexedstring[i+2][0] == 'END_LINE':
        name = lexedstring[i+1][1]
        i += 3
        i,itemlist = room_desc(i,lexedstring)
        return i,Item(Chars(name),itemlist)
    else:
        raise ParsingError('Does not contain the proper fromat for an object')
        
def guard(i,lexedstring):
    if lexedstring[i][0] == 'NEW_GUARD' and lexedstring[i+1][0] == 'CHARS' and lexedstring[i+2][0] == 'GUARD_LIMIT':
        conditions = lexedstring[i+1][1]
        i += 3
        i,itemlist = room_desc(i,lexedstring)
        if lexedstring[i][0] == 'GUARD_LIMIT':
            i +=1
            return i,Guard(Chars(conditions),itemlist)
        else:
            raise ParsingError('not a guard')
    else:
        raise ParsingError('not a guard')

def variable(i,lexedstring):
    if lexedstring[i][0] == 'OPEN_SCRIPT' and lexedstring[i + 1][0] == 'CHARS' and lexedstring[i + 2][0] == 'CLOSE_SCRIPT':
        return i+3,Variable(Chars(lexedstring[i + 1][1]))
    else:
        raise ParsingError('not a variable')