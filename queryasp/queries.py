# -*- coding: utf-8 -*-
"""Query operators"""

from __future__ import print_function
from abc import ABCMeta, abstractmethod
import re
from pyparsing import infixNotation, opAssoc, Word, Suppress
import pyparsing as pp
import clingo
from queryasp.session import Command
from queryasp.aux import debug, on_model

COMMANDS = ['Query']
# SPEC = dict.fromkeys(['Query'], None)

class Query(Command): #TODO: subclass Command
    """Query operator."""

    ext_atom = '_qext-1'
    session_step = -1

    def __init__(self, session, stdout):
        super(self.__class__, self).__init__(session, stdout, share_keys={'show_preds' : set()})

    def apply(self, qexpr, *args, **kwargs):
        """Applies query."""
        Query.ext_atom = self._gen_ext_atom()
        Query.session_step = self._session.step
        prg = self._session.state.prg
        enc_name = "query_" + str(self._session.step + 1)
        parse_result = QueryParser.queryexp.parseString(qexpr, True)
        parse_result_str = str(parse_result).strip("[]")
        parse_result_str = re.sub(r'\(\S*\)', '', parse_result_str.split()[0]) + " " + parse_result_str.split(' ', 1)[1] # TODO: Hack to flatten top-level head. Adjust semantic action/parser to omit vars in body of top-level head
        debug(parse_result_str, "Query.apply: parse_result")
        prg.add(enc_name, [], parse_result_str)  # equivalent rules for query expr
        prg.add(enc_name, [], "#external {0}.".format(Query.ext_atom))  # external atom switch
        prg.ground([(enc_name, [])])
        prg.assign_external(clingo.Function(Query.ext_atom), True)
        query_head = clingo.Function(parse_result_str.split()[0])
        debug(query_head, "Query.apply: query_head")
        assumptions = list(self._session.state.assumptions) # copy of assumptions to add query head atom for solving
        assumptions.append((query_head, True))
        output_on_model = [] # output returned by on_model
        self._session.state.prg.solve(on_model(self._shared_data['show_preds'], output_on_model), assumptions)
        self.prnt('\n'.join(output_on_model) + '\n')
        prg.release_external(clingo.Function(Query.ext_atom))
        self._update_session_log("query", "qexpr", qexpr)

    def _gen_ext_atom(self):
        """Generate external atom switch to be used in each rule body"""
        return "_qext" + str(self._session.step + 1)


class BoolNode(object):
    """Abstract class for sub-expressions that reassemble a node in the Boolean operator tree."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, t):
        self.qatom_prefix = "_q" + str(Query.session_step)

    def __str__(self):
        return self.gen_rules()     

    @abstractmethod
    def gen_head_atom(self):
        pass

    def flatten_head_atom(self, head, noVarArgs=False):
        """Aux method for `gen_head_atom` to make a head_atom a non-nested term

        Achieved by simply replacing
        - parenthesis with '_lpar_' and '_rpar_'.
        - commas and semicolons with _sepr_
        - whitespace occurring before/after arguments within parentheses stripped
        Additionally, all occurring variables are collected and added as arguments of a new body

        """
        head = head.replace("(", "_lpar_")
        head = head.replace(")", "_rpar_")
        head = head.replace(",", "_sepr_")
        head = head.replace(";", "_sepr_")
        head = head.replace(" ", "")

        matchlist = re.findall(r'(AND|OR|NOT)|([A-Z][a-zA-Z0-9]*)', head)
        varlist = list(set(m[1] for m in matchlist if m[1] != '')) # extract only vars and unify
        debug(varlist, 'varlist')
        if varlist and not noVarArgs:
            head = '{0}({1})'.format(head, ','.join(varlist))

        return head

    @abstractmethod
    def gen_rules(self):
        pass

    __repr__ = __str__


class BoolOperand(BoolNode):
    """Parse action for query atoms

    Note that query atoms are the Boolean operands (domain elements for Boolean operations)
    in query expression.
    """

    def __init__(self, t):
        super(BoolOperand, self).__init__(t)
        self.label = t[0].strip()

    def gen_head_atom(self):
        # return self.qatom_prefix + "\'" + self.label + "\'"
        head = self.qatom_prefix + self.label
        return self.flatten_head_atom(head)

    def gen_rules(self):
        return  "{0} :- {1}; {2}.\n".format(self.gen_head_atom(), self.label, Query.ext_atom)



class BoolBinOp(BoolNode):

    def __init__(self, t):
        super(BoolBinOp, self).__init__(t)
        self.args = t[0][0::2]
       # self.reprsymbol = None

    def __str__(self):
        return self.gen_head_atom()

    @abstractmethod
    def gen_head_atom(self):
        """Head atom specific to bin op"""
        pass

    def gen_rules(self):
        # sub_expr_rules = ""
        # for arg in self.args:
        #     sub_expr_rules += arg.gen_rules()
        sub_expr_rules = "".join(arg.gen_rules() for arg in self.args)
        return self.gen_binoprules() + sub_expr_rules

    @abstractmethod
    def gen_binoprules(self):
        """Rule specific to this bin op"""
        pass


class BoolAnd(BoolBinOp):

    def __init__(self, t):
        super(BoolAnd, self).__init__(t)
        self.reprsymbol = '; '

    def gen_head_atom(self):
        head = self.qatom_prefix + "_AND_".join(arg.gen_head_atom() for arg in self.args)
        return self.flatten_head_atom(head)

    def gen_binoprules(self):
        return "{0} :- {1}; {2}.\n".format(self.gen_head_atom(),
                                           self.reprsymbol.join(arg.gen_head_atom() for arg in self.args),
                                           Query.ext_atom)


class BoolOr(BoolBinOp):

    def __init__(self, t):
        super(BoolOr, self).__init__(t)
        self.reprsymbol = '|'

    def gen_head_atom(self):
        head = self.qatom_prefix + "_OR_".join((arg.gen_head_atom() for arg in self.args))
        return self.flatten_head_atom(head)

    def gen_binoprules(self):
        rules = ""
        for arg in self.args:
            rules += "{0} :- {1}; {2}.\n".format(self.gen_head_atom(), arg.gen_head_atom(), Query.ext_atom)
        return rules


class BoolNot(BoolNode):

    def __init__(self, t):
        super(BoolNot, self).__init__(t)
        self.arg = t[0][1]
        self.reprsymbol = 'not'

    def gen_head_atom(self):
        head = self.qatom_prefix + "NOT_" + str(self.arg.gen_head_atom())
        return self.flatten_head_atom(head)

    def gen_rules(self):
        sub_expr_rules = self.arg.gen_rules()
        not_op_rules = "{0} :- not {1}; {2}.\n".format(self.gen_head_atom(), self.arg.gen_head_atom(), Query.ext_atom)
        return not_op_rules + sub_expr_rules


class QueryParser(object):

    legalcontchars= pp.printables.replace("[",'').replace("]",'').replace("&",'').replace("|",'')
    legalcontcharsws= legalcontchars + " "
    #atom = pp.Combine(pp.Word(legalcontchars, exact=1) + (Word(legalcontcharsws) + pp.Word(legalcontchars, exact=1))*(0,None))
    atom =  Word(legalcontcharsws)
    atom.setParseAction(BoolOperand)
    #atom.setDebug(True)

    queryexp = infixNotation( atom,
                              [
                                  ("not", 1, opAssoc.RIGHT, BoolNot),
                                  ("&", 2, opAssoc.LEFT, BoolAnd),
                                  ("|", 2, opAssoc.LEFT, BoolOr),
                              ],
                              lpar=Suppress("["),
                              rpar=Suppress("]"),
                          )

    atom_raw = Word(legalcontcharsws)
    queryexp_raw = infixNotation( atom_raw,
                              [
                                  ("not", 1, opAssoc.RIGHT),
                                  ("&", 2, opAssoc.LEFT),
                                  ("|", 2, opAssoc.LEFT),
                              ],
                              lpar=Suppress("["),
                              rpar=Suppress("]"),
                          )


    @staticmethod
    def test():

        query=\
               "[aa(s(_6d42,ad5),_s(d)) & as(da3,56H,sdb) & not 45_c( as, da) | [casd(S,DFD) & sd(SDFS)] ]"
        query2="[ 7+3=a(X) ]"
        query3="[ bc & bc ]"
        query4="[ _b(c=[asd##$a&]&|+) & c(#$%#) ]"
        query5="[ d(v, d) & b( c, e) | not c(df,g)]"
        query6="[ d(a) ]"
        query7="bsdfs(sdf, we , dfg) & _bdsfgs_(_sdfs(sdf), 345(34))"
        query8= "a & b | c & d"
        query9= "not a & b | not c & d"
        query10= "a & [b | not c]"
        query11= "not a | b"
        query12= "not a & b"
        query13= "not a"
        query14= "a"
        query15= "a(X) & b(X,Y2) & c(Y2,Z,W1)"
        #queryexp.setDebug(True)
        thequery= query15
        result =  QueryParser.queryexp.parseString(thequery,True)
        result_raw = QueryParser.queryexp_raw.parseString(thequery,True)
        print ("\n\n**Input query:\n" + thequery)
        print ("\n\n**Result:\n" + str(result.asList()))
        #print ("\n\n**Result dump:\n" + result.dump())
        print ("\n\n**Result w/o actions:\n" + result_raw.asXML())
        print ("\n\n**Result raw dump:\n" + str(result_raw.dump()))

# queryasp.aux.DEBUG = True
# QueryParser.test()
