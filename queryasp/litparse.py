"""Literal Parser

Parses nested structure of literal formulas and builds corresponding
clingo.Function object

"""

from __future__ import print_function
import sys
from abc import ABCMeta, abstractmethod
from queryasp.session import Session, State
import queryasp.aux
from queryasp.aux import debug
from pyparsing import infixNotation, opAssoc, Keyword, Word, alphas, alphanums, Literal, Suppress
import pyparsing as pp
import pprint
import clingo
import re
import pprint


ResultTopObject = None #TODO: move into parser object

class PA_LitSubExpr(object):
    """Generic class for sub-expressions occurring in a literal."""
    __metaclass__ = ABCMeta
    
    def __init__(self, t):
        self.label = str(t)
        debug("")
        debug("","Next object")
        debug("Object " + type(self).__name__ + " " + str(self))
        debug("All sub-items")
        for item in t:
            debug(type(item), item.asList() if isinstance(item,pp.ParseResults) else item)

    def __str__(self):
        return self.label

    __repr__ = __str__


class PA_Num(PA_LitSubExpr):

    def __init__(self, t):
        super(PA_Num, self).__init__(t)
        self.ggfun = int(t[0]) #clingo.Function(t[0])
        debug ("ggfun " + type(self.ggfun).__name__ + " " + str(self.ggfun))

    def __str__(self):
        return "Num " + self.label


class PA_Functionc(PA_LitSubExpr):

    def __init__(self, t):
        super(PA_Functionc, self).__init__(t)
        arg_fun_objects = []
        try:
            arg_fun_objects = list(arg.ggfun for arg in t[0][1])
        except IndexError:
            pass
        if arg_fun_objects:
            self.ggfun = clingo.Function(t[0][0], arg_fun_objects)
        else:
            self.ggfun = clingo.Function(t[0][0])
        debug("ggfun " + type(self.ggfun).__name__ + " " + str(self.ggfun))

    def __str__(self):
        return "Functionc " + self.label


class PA_Literal(PA_LitSubExpr):

    def __init__(self, t):
        global ResultTopObject
        super(PA_Literal, self).__init__(t)
        self.dneg = False
        if isinstance(t[0], str) and t[0] == 'not ':
            self.dneg = True
            self.ggfun = t[1].ggfun
        else:
            self.ggfun = t[0].ggfun
        ResultTopObject = self
        debug("ggfun " + type(self.ggfun).__name__ + " " + str(self.ggfun))
        if self.dneg:
            debug("has default neg!\n")
       
    def __str__(self):
        return "Literal " + self.label




class LiteralParser(object):

    # Grammar
    @staticmethod
    def grammar_annotated():
        dneg = pp.Literal('not ').setName('dneg')
        name = pp.Combine(pp.Literal('-')*(0, 1) +
                          pp.Word(pp.srange('[a-z_]')) +
                          pp.Word(pp.alphanums + '_')*(0, 1)).setName('name')
        lpar = pp.Suppress('(')
        rpar = pp.Suppress(')')
        sepr = pp.Suppress(';') | pp.Suppress(',')
        num = pp.Word(pp.nums).setName('num')
        # arg_body = pp.nestedExpr(opener='(', closer=')', content=pp.Word(pp.alphanums)).setResultsName('arg_body')
        arg_body = pp.Forward()
        literal = pp.Forward()
        func = pp.Forward()
        term = pp.Forward()
        term <<= (func('func*') | num('num_arg*'))
        arg_body <<= pp.Group(lpar + ((term + (sepr + term)*(0, None)) | pp.empty()) + rpar)
        func <<= pp.Group(name('fname') + arg_body.setResultsName('fbody')*(0, 1))('func')
        literal <<= (dneg('dneg')*(0, 1) + func('atom'))('literal')     
        return literal

    @staticmethod
    def grammar():
        dneg = pp.Literal('not ')
        name = pp.Combine(pp.Literal('-')*(0, 1) +
                          pp.Word(pp.srange('[a-z_]')) +
                          pp.Word(pp.alphanums + '_')*(0, 1))
        lpar = pp.Suppress('(')
        rpar = pp.Suppress(')')
        sepr = pp.Suppress(';') | pp.Suppress(',')
        num = pp.Word(pp.nums)
        # arg_body = pp.nestedExpr(opener='(', closer=')', content=pp.Word(pp.alphanums)).setResultsName('arg_body')
        arg_body = pp.Forward()
        literal = pp.Forward()
        func = pp.Forward()
        term = pp.Forward()
        term <<= (func | num)
        arg_body <<= pp.Group(lpar + ((term + (sepr + term)*(0, None)) | pp.empty()) + rpar)
        func <<= pp.Group(name + arg_body*(0, 1))
        literal <<= (dneg*(0, 1) + func)

        #Semantic Actions
        func.setParseAction(PA_Functionc)
        num.setParseAction(PA_Num)
        literal.setParseAction(PA_Literal)
        
        return literal
    
    @staticmethod
    def test(parser):
        a1 = "a(1, 4fs_ad)"
        a2 = "not a"
        a3 = "not a(a1; nota4_Sfsad; bsd(1,asd;65))"
        a4 = "a(b(c(uwer(s, r(443)),_d(e, a45(g)))))"
        a5 = "a(b,c)"
        a6 = "not a(c,a1)"
        a7 = "a()"
        a8 = "a(1,c2,3,df4,5,6) "
        a9 = "a(b,c(d),12)"
        a10 = "a(1)"
        a11 = "not icolor(1,r)"

        thelit = a9

        queryasp.aux.DEBUG = True
        parser.setDebug(True)

        result = parser.parseString(thelit, True)
        print ("\n\n**Input literal:\n" + thelit)
        print ("\n\n**Result Dump:\n" + str(result.dump()))
        print ("\n\n**Result:\n" + str(result))

        print("ResultTopObject: " + str(ResultTopObject.ggfun))
        myfun = clingo.Function("a", [clingo.Function("b")])
        print("myfun: " + str(myfun))

        prg = clingo.Control()
        theatom = thelit
        if thelit.startswith('not '):
            theatom = thelit[len('not '):]
        prg.add('base', [], "#external {0}. ext_true :- {0}. ext_false :- not {0}.".format(theatom))
        prg.ground([("base", [])])
        #prg.assign_external(clingo.Function("a",[1]), True)
        prg.assign_external(ResultTopObject.ggfun, not ResultTopObject.dneg)
        prg.solve(on_model=(lambda m: print("Model: " + str(m.atoms()))))


#LiteralParser.test(LiteralParser.grammar())
