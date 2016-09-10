# -*- coding: utf-8 -*-
"""Experimental state-changing operators"""

from __future__ import print_function
from abc import ABCMeta, abstractmethod
from queryasp.session import Session, State
from queryasp.aux import debug
import clingo

from queryasp.scops import StateChangingOp

class AssertPlus(StateChangingOp):
    """Assertion operator."""

    def apply(self, atom, *args, **kwargs):
        assertions = self._session.state.assertions
        prg = self._session.state.prg
        ext_atom = "_ext_assert__{0}".format(atom)
        if not assertions.has_key(atom):
            enc_name = "assertion_" + atom
            prg.add(enc_name, [], "{0} :- {1}. #external {1}.".format(atom, ext_atom))
            prg.ground([(enc_name, [])])
            assertions[atom] = [ext_atom, 1]
        elif assertions[atom][0] != ext_atom:
            raise Exception("Bug: asserted atom exists in assertion list with different external!")
        prg.assign_external(clingo.Function(ext_atom), True)
        self._update_session_log("assert", "atom", {atom: ext_atom})
        debug(str(self._session.state.assertions))


class RetractPlus(StateChangingOp):
    """Retraction operator."""

    def apply(self, atom, *args, **kwargs):
        prg = self._session.state.prg
        assertions = self._session.state.assertions
        if assertions.has_key(atom):
            ext_atom = self._session.state.assertions[atom][0]
            prg.assign_external(clingo.Function(ext_atom), False)
            assertions[atom][1] = 0
        else:
            print("Atom {0} not asserted!".format(atom))
        self._update_session_log("retract", "atom", atom)
        debug(str(self._session.state.assertions))
