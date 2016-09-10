# -*- coding: utf-8 -*-
"""State-changing operators"""

from __future__ import print_function
import re
from abc import ABCMeta
from queryasp.session import Command
from queryasp.aux import debug
import queryasp.litparse as litparse

COMMANDS = ['Assert', 'Retract', 'Open', 'Assume', 'Cancel', 'External',
            'Release', 'Define', 'DefineDyn', 'Filter', 'Load', 'Reset']

# SPEC = dict.fromkeys(['Assert', 'Retract', 'Open', 'Assume', 'Cancel',
#                       'External', 'Release', 'Define', 'DefineDyn', 'Filter', 'Load',
#                       'Reset'], None)


class StateChangingOp(Command):
    """General class for state changing operators."""
    __metaclass__ = ABCMeta

    def parse_literal(self, literal):
        """Parse literal to corrseponding `clingo.Function` object and Sign"""
        parse_result = litparse.LiteralParser.grammar().parseString(literal, True)
        debug(parse_result, "Parse Result: ")
        return litparse.ResultTopObject.ggfun, not litparse.ResultTopObject.dneg


class Assert(StateChangingOp):
    """Assertion operator."""
    def apply(self, atom, *args, **kwargs):
        #self.session.state.prg.assign_external(clingo.Function(atom), True)
        ggfun = self.parse_literal(atom)[0]
        self._session.state.prg.assign_external(ggfun, True)
        debug(ggfun, "Asserting: ")
        self._update_session_log("assert", "atom", atom)


class Retract(StateChangingOp):
    """Retraction operator."""
    def apply(self, atom, *args, **kwargs):
        #self.session.state.prg.assign_external(clingo.Function(atom), False)
        ggfun = self.parse_literal(atom)[0]
        self._session.state.prg.assign_external(ggfun, False)
        debug(ggfun, "Retracting: ")
        self._update_session_log("retract", "atom", atom)


class Open(StateChangingOp):
    """Open operator."""

    def apply(self, atom, *args, **kwargs):
        #self.session.state.prg.assign_external(clingo.Function(atom), False)
        ggfun = self.parse_literal(atom)[0]
        self._session.state.prg.assign_external(ggfun, None)
        debug(ggfun, "Opening: ")
        self._update_session_log("open", "atom", atom)


class Assume(StateChangingOp):
    """Assumption operator."""
    def apply(self, literal, *args, **kwargs):
        assumptions = self._session.state.assumptions
        ggfun_and_sign = self.parse_literal(literal)
        if ggfun_and_sign not in assumptions:
            assumptions.append(ggfun_and_sign)
        else:
            self.prnt("Literal {0} already assumed!".format(literal))
        self._update_session_log("assume", "literal", literal)
        debug(str(assumptions), "session.state.assumptions")


class Cancel(StateChangingOp):
    """Cancel  operator."""

    def apply(self, literal, *args, **kwargs):
        assumptions = self._session.state.assumptions
        ggfun_and_sign = self.parse_literal(literal)
        if ggfun_and_sign in assumptions:
            assumptions.remove(ggfun_and_sign)
        else:
            self.prnt("Literal {0} was not assumed!".format(literal))
        self._update_session_log("cancel", "literal", literal)
        debug(str(assumptions), "session.state.assumptions")


class External(StateChangingOp):
    """External operator."""
    def apply(self, atom, *args, **kwargs):
        prg = self._session.state.prg
        enc_name = "ext_" + atom + str(self._session.step + 1)
        prg.add(enc_name, [], "#external {0}.".format(atom))
        prg.ground([(enc_name, [])])
        self._update_session_log("external", "atom", atom)


class Release(StateChangingOp):
    """Release operator."""
    def apply(self, atom, *args, **kwargs):
        ggfun = self.parse_literal(atom)[0]
        self._session.state.prg.release_external(ggfun)
        self._update_session_log("release", "atom", atom)


class Define(StateChangingOp):
    """Define operator."""
    def __init__(self, session, stdout):
        super(self.__class__, self).__init__(session, stdout)
        self.frontend_conf['cmd2']['multiline'] = True

    def apply(self, rules, *args, **kwargs):
        """Adds rules to the session's program.

        Addition via clingo.Control.add()

        Arguments:
        rules -- program in clingo syntax to add
        """
        prg = self._session.state.prg
        enc_name = "define_" + str(self._session.step + 1)
        prg.add(enc_name, [], rules)
        # TODO: catch syntax error exception after adding an erroneous
        # program, which cannot be removed and hence yields an
        # irrecoverable grounding error --> feature request clingo
        # API: prg.remove as inversion of add if not grounded yet
        prg.ground([(enc_name, [])])
        self._update_session_log("define", "rules", rules)


class DefineDyn(StateChangingOp):
    """DefineDyn operator."""
    def __init__(self, session, stdout):
        super(self.__class__, self).__init__(session, stdout, local_data=dict(dynrules=list()))
        self.frontend_conf['cmd2']['multiline'] = True

    def apply(self, raw, *args, **kwargs):
        """Application depending on the type of args."""
        rules_dat = self._data['dynrules']
        match_toggle = re.match(r'\s*(on|off)\s+([[0-9]*)\s*', raw)
        if match_toggle: # Turn ON/OFF previously defined dynamic program
            ext_tv = False
            if match_toggle.group(1) == 'on':
                ext_tv = True
            handle = match_toggle.group(2)
            ext_atom = ''
            try:
                ext_atom = rules_dat[int(handle)][1]
            except IndexError:
                self.prnt("Dynamic program with handle {0} does NOT exist!".format(handle))
                self._update_session_log("definedyn", match_toggle.group(1), handle)
                return
            ggfun = self.parse_literal(ext_atom)[0]
            debug(ggfun, "Assigning {0} to: ".format(str(ext_tv)))
            self._session.state.prg.assign_external(ggfun, ext_tv)
            if ext_tv:
                rules_dat[int(handle)][2] = 'on'
                self.prnt('Turned ON dynamic program with handle {0}.'.format(handle))
            else:
                rules_dat[int(handle)][2] = 'off'
                self.prnt('Turned OFF dynamic program with handle {0}.'.format(handle))
            self._update_session_log("definedyn", match_toggle.group(1), handle)
        elif raw: # Define new dynamic program
            self._add_rules(raw)
        else: # Print out existing dynamic programs
            output = 'List of dynamically added programs:\n'
            for i in range(len(rules_dat)):
                output += '\n**Dynamic-Program {0} ({2}):\n{1}\n'.format(str(i),
                                                                         rules_dat[i][0],
                                                                         rules_dat[i][2])
            self.prnt(output)


    def _add_rules(self, rules): #TODO Merge with filter variant
        """Dynamical adds rules to the session's program.

        Addition via clingo.Control.add(). Each rule in rules is
        modified by adding a designated 'toggle' external atom.

        Arguments:
        rules  -- program in clingo syntax to add

        """
        handle = str(len(self._data))
        prg = self._session.state.prg
        ext_atom = '_ddext' + handle
        enc_name = 'definedyn_' + handle
        rules = rules.replace('.', '.\n')
        self._data['dynrules'].append([rules, ext_atom, 'off'])
        prg.add(enc_name, [], "#external {0}.".format(ext_atom))
        prg.add(enc_name, [], self._inject_external(rules, ext_atom))
        prg.ground([(enc_name, [])])
        self.prnt("Defined dynamic program with handle {0}.".format(handle))
        self._update_session_log("definedyn", "rules", rules)

    def _inject_external(self, rules, ext):
        """Adds external to rule bodies."""
        rewrite = ''
        for line in rules.splitlines():
            if line.find(':-') != -1:
                rewrite += line.replace('.', '; {0}.'.format(ext))
            else:
                rewrite += line.replace('.', ' :- {0}.'.format(ext))
        debug(rewrite, '_inject_external')
        return rewrite
        # TODO: fragile, does not work for rules that use '.' within rule:
        # - when using string constants that contain '.' , e.g. a("1.3").
        # - domain range specifications, e.g. X=1..100
        # - etc.
        # Solution: parse with clingo rule grammar.


class Filter(StateChangingOp):
    """Filter operator.

    - Syntax: filt min/max <term tuple with weights priorities and safety literals>
    - Implemented as view on Definedyn
    """

    def __init__(self, session, stdout):
        super(self.__class__, self).__init__(session, stdout, local_data=dict(opt_stmts=list()))

    def apply(self, raw, *args, **kwargs):
        """Application depending on the type of args."""
        opt_dat = self._data['opt_stmts']
        match_toggle = re.match(r'\s*(on|off)\s+([[0-9]+)\s*', raw)
        match_opt = re.match(r'\s*(min|max)\s+(.+)', raw)
        if match_toggle: # Turn ON/OFF previously defined dynamic program
            ext_tv = False
            if match_toggle.group(1) == 'on':
                ext_tv = True
            handle = match_toggle.group(2)
            ext_atom = ''
            try:
                ext_atom = opt_dat[int(handle)][1]
            except IndexError:
                self.prnt("Dynamic program with handle {0} does NOT exist!".format(handle))
                self._update_session_log("filter", match_toggle.group(1), handle)
                return
            ggfun = self.parse_literal(ext_atom)[0]
            debug(ggfun, "Assigning {0} to: ".format(str(ext_tv)))
            self._session.state.prg.assign_external(ggfun, ext_tv)
            if ext_tv:
                opt_dat[int(handle)][2] = 'on'
                self.prnt('Turned ON dynamic program with handle {0}.'.format(handle))
            else:
                opt_dat[int(handle)][2] = 'off'
                self.prnt('Turned OFF dynamic program with handle {0}.'.format(handle))
            self._update_session_log("filter", match_toggle.group(1), handle)
        elif match_opt:# Add optimization as filter
            self._add_opt(match_opt.group(1), match_opt.group(2))
        elif raw: # Add weak constraint (i.e. #minimize statement with a single <term tuple, body-literals>-pair ) as filter
            self._add_opt('min', raw)
        else: # Print out existing filter programs
            output = 'List of dynamically added optimization statements:\n'
            for i in range(len(opt_dat)):
                output += '\n**Filter-Program {0} ({2}):\n{1}\n'.format(str(i),
                                                                        opt_dat[i][0],
                                                                        opt_dat[i][2])
            self.prnt(output)


    def _add_opt(self, opt, ttblpairs): #TODO: merge with variant from DefineDyn
        """Dynamical adds optimization statement to the session's program.

        Addition via clingo.Control.add(). Each rule in rules is
        modified by adding a designated 'toggle' external atom.

        Arguments:
        opt         -- optimization type, i.e., either 'min' or 'max'
        ttblpairs  -- the <term tuple, body-literals>-pairs to be used as optimization argument

        """
        handle = str(len(self._data['opt_stmts']))
        prg = self._session.state.prg
        ext_atom = '_optext' + handle
        enc_name = 'filter_' + handle
        optkw = '#maximize' if opt == 'max' else '#minimize'
        rule = '{0}{{{1}}}.'.format(optkw, ttblpairs)
        self._data['opt_stmts'].append([rule, ext_atom, 'off'])
        prg.add(enc_name, [], "#external {0}.".format(ext_atom))
        prg.add(enc_name, [], self._inject_external(rule, ext_atom))
        prg.ground([(enc_name, [])])
        self.prnt("Defined dynamic filter with handle {0}.".format(handle))
        self._update_session_log("filter", opt, ttblpairs)


    def _inject_external(self, rule, ext):
        """Adds external to literal list bodies of terms."""
        rewrite = rule.replace(':', ':{0},'.format(ext))
        debug(rewrite, '_inject_external')
        return rewrite


class Load(StateChangingOp):
    # TODO: No(!) State reset but extend rules R of the State (R,I,i,j).
    """Load encoding(s) from file(s) and re-initialize state with it

    - Solver options set by initial cl flags carry over
    - Only 'base' programs supported!

    """
    def __init__(self, session, stdout):
        super(self.__class__, self).__init__(session, stdout)

    def apply(self, prg_files, *args, **kwargs):
        """Adds rules to the session's program via clingo.Control.load()

        Arguments:
        prg_files -- list of program files to load
        """
        # self._session.reset_state(prg_files.split())# TODO: no reset but extension of R
        prg = self._session.state.prg
        for fname in prg_files.split():
            prg.load(fname)
        prg.ground([("base", [])])
        self._update_session_log("load", "prg_files", prg_files)


class Reset(StateChangingOp):
    """Resets state with optionally new encoding and solver_opts.

    - Otherwise, initial solver options and encoding given at aspic's
      invocation as cl pars are re-used.
    - Only 'base' programs supported!

    """
    def __init__(self, session, stdout):
        super(self.__class__, self).__init__(session, stdout)

    def apply(self, raw=None, *args, **kwargs): #TODO maybe explicit raw parser of all Command
        """Resets session's state

        Arguments:
        prg_files -- list of program files to load

        """
        if raw.find(' -o') != -1:
            prg_files, solve_opts = raw.split(' -o')
            self._session.reset_state(prg_files.strip(' ').split(), solve_opts.strip(' '))
        elif raw:
            self._session.reset_state(raw.split())
        else:
            self._session.reset_state()
        self._update_session_log("reset", "prg_files", raw)
