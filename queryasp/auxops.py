# -*- coding: utf-8 -*-

from __future__ import print_function
import re
from queryasp.aux import debug, on_model, on_finish
from queryasp.session import Command

COMMANDS = ['Option', 'Show', 'Hide', 'Solve']
#SPEC = dict.fromkeys(['Option', 'Show', 'Hide', 'Solve'], None)

RE_RELSIG = re.compile(r'(\w+)(/(\d+))?')

class Option(Command):
    """Passes cl options to clingo object."""

    def apply(self, raw, *args, **kwargs):
        prg = self._session.state.prg
        debug(raw, "queryasp.auxops.Option, received args")
        re_models = re.compile(r'(--models|-n)\s*(\d+)')
        re_enum_mode = re.compile(r'(--enum-mode|-e)\s*(\w+)')
        re_opt_mode = re.compile(r'(--opt-mode)\s*(\w+)')
        if re_models.match(raw):
            prg.conf.solve.models = re_models.match(raw).group(2)
        elif re_enum_mode.match(raw):
            prg.conf.solve.enum_mode = re_enum_mode.match(raw).group(2)
        elif re_opt_mode.match(raw):
            prg.conf.solve.opt_mode = re_opt_mode.match(raw).group(2)
        else:
            self.prnt("Clingo command line option ({0}) not supported!".format(raw))


class Show(Command):
    """Show aux command."""

    def __init__(self, session, stdout, **kwargs):
        super(self.__class__, self).__init__(session, stdout, share_keys={'show_preds' : set()}, **kwargs)

    def apply(self, raw, *args, **kwargs):
        show = self._shared_data['show_preds']
        if not raw:
            if show:
                self.prnt('\n'.join(str(sig) for sig in show))
            else:
                self.prnt('All atoms are shown (i.e., no predicate signatures selected via the \'show\' command)')
        elif raw.startswith('-r'):
            predsigs = raw.split()[1:]
            if predsigs:
                for sig in predsigs:
                    show.discard(predsigs)
            else:  # clear all show atoms when no args give
                show.clear()
        else:
            for sig in raw.split():
                if RE_RELSIG.match(sig):
                    show.add(sig)
                else:
                    raise Exception('Wrong predicate signature format!')


class Hide(Command):
    """Hide aux command."""

    def __init__(self, session, stdout, **kwargs):
        super(self.__class__, self).__init__(session, stdout, share_keys={'show_preds' : set()}, **kwargs)

    def apply(self, predsigs, *args, **kwargs):
        show = self._shared_data['show_preds']
        if predsigs:
            sigs = predsigs.split()
            if sigs:
                for sig in sigs:
                    show.discard(sig)
        else:  # clear all show atoms when no args give
            show.clear()
            self.prnt('''All atoms will be shown again (i.e., list of predicate signatures of 'show' command cleared).''')


class Solve(Command):
    """Solve command"""

    def __init__(self, session, stdout, **kwargs):
        super(self.__class__, self).__init__(session, stdout, share_keys={'show_preds' : set()}, **kwargs)
        self.frontend_conf['cmd2']['callback'] = lambda raw: self.apply() # Redundant example implementation of custom callback funct

    def apply(self, raw=None, *args, **kwargs):
        """Prints models and sat result"""
        output_on_model = [] # output returned by on_model
        solve_future = self._session.state.prg.solve_async(on_model(self._shared_data['show_preds'], output_on_model),
                                                           on_finish,
                                                           self._session.state.assumptions)
        output_sat = str(solve_future.get()) # sat result returned by solve
        self.prnt('\n'.join(output_on_model) + '\n' + output_sat)
