#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import argparse
import cmd2
import sys
import queryasp.aux
from queryasp.aux import debug, on_model#, option, show, hide, Option
from queryasp import release

#sys.path.insert(0, '..')  # puts root dir in front of sys.path for import
from queryasp.session import Session
from queryasp.scops import Assert, Retract, Open, Assume, Cancel, External, Release, Define, DefineDyn, Filter, Load
from queryasp.queries import Query
from queryasp.auxops import Option, Show, Hide, Solve

class CmdLineApp(cmd2.Cmd, object):
    """Command line interpreter main class."""

    #cmd2 settings
    #intro = "Welcome to ASPIC 0.1"
    prompt = "?- "
    multilineCommands = ['define', 'definedyn']
    terminators = ['?']
    defaultExtension = 'aic'            # For ``save``, ``load``, etc.
    default_file_name = 'command.aic'   # For ``save``, ``load``, etc.

    #List of aspic custom commands
    custom_commands = ['option', 'solve', 'show', 'hide', 'assert', 'retract', 'assume',
                       'cancel', 'open', 'external', 'release', 'define', 'definedyn',
                       'query', 'filter']

    #List of aspic custom commands that need quoted args body
    custom_commands_quoted_args = [cc for cc in custom_commands if not cc in multilineCommands]

    def __init__(self, prg_files=None, solve_opts=""):
        """Initialize CmdLineApp object.

        Arguments:
        prg_files     -- program file names to load (default [])
        solve_options -- solve options for clingo (default [])

        """
        print("Welcome to {0} {1}".format(release.name, release.__version__))
        super(self.__class__, self).__init__()
        self.session = Session(self.stdout, prg_files or [], solve_opts)

    def preparse(self, raw, **kwargs):
        """Overriding `cmd2.preparse` hook to single-quote arguments for the query
        command.

        This is necessary to prevent certain symbols to be recognized
        as built-in keywords by `cmd2.parser`

        """
        aspic_exp = raw
        pipe = ''

        # Split off part that should piped to OS shell, indicated by '\|''
        if raw.find('\|') != -1:
            aspic_exp, pipe = raw.split('\|', 1)

        # Quote aspic args if necessary
        if ' ' in aspic_exp.strip(' '):
            command, args = aspic_exp.split(' ', 1)
            if command.strip(' ') in CmdLineApp.custom_commands_quoted_args:
                rewrite = "{0} '{1}'".format(command, args)
                if pipe:
                    rewrite = rewrite + '|' + pipe
                debug(rewrite, "ClApp.preparse return val")
                return rewrite
        return raw

    @staticmethod
    def cond_rm_quotes(cmd, qraw):
        """Remove quotes from arguments quoted by function 'preparse'

        Arguments:
        cmd  -- command name
        qraw -- quoted, raw string of arguments
        """
        if cmd in CmdLineApp.custom_commands_quoted_args:
            return qraw[1:-1]
        else:
            return qraw


    #
    # Aux Ops
    #
    def do_load(self, prg_files): #Overrides Cmd.do_load from cmd2!
        """Restarts clingo (new clingo.Control object) and loads ASP program from given path.

        Arguments:
        prg_files -- white-space separated list of paths to ASP programs to load
        """
        Load(self.session, self.stdout).apply(self.cond_rm_quotes('show', raw))

    def do_exec(self, arg=None): #Renamed invocation wrapper of Cmd.do_load from cmd2!
        """Runs an aspic shell script at given path.

        Arguments:
        arg -- path to aspic script to run
        """
        super(self.__class__, self).do_load(arg)

    def do_option(self, raw):
        """Call option in current state.

        Passes command line options to the solver of the embodied
        clingo object

        Supported Arguments:
        --enum_mode,-e <arg> -- configure enumeration algorithm, .e.g brave/cautious consequences
        --models,-n <n>      -- compute at most <n> models
        """
        Option(self.session, self.stdout).apply(self.cond_rm_quotes('option', raw))

    def do_solve(self, raw):
        """Call solve in current state."""
        Solve(self.session, self.stdout).apply(self.cond_rm_quotes('show', raw))

    def do_show(self, raw):
        """Call show in current state."""
        Show(self.session, self.stdout).apply(self.cond_rm_quotes('show', raw))

    def do_hide(self, raw):
        """Call hide in current state."""
        Hide(self.session, self.stdout).apply(self.cond_rm_quotes('hide', raw))


    #
    # State-changing Ops
    #
    def do_assert(self, raw):
        """Call assert in current state."""
        Assert(self.session, self.stdout).apply(self.cond_rm_quotes('assert', raw)) # TODO: condense into one call

    def do_retract(self, raw):
        """Call retract in current state."""
        Retract(self.session, self.stdout).apply(self.cond_rm_quotes('retract', raw))

    def do_open(self, raw):
        """Call open in current state."""
        Open(self.session, self.stdout).apply(self.cond_rm_quotes('open', raw))

    def do_assume(self, raw):
        """Call assume in current state."""
        Assume(self.session, self.stdout).apply(self.cond_rm_quotes('assume', raw))

    def do_cancel(self, raw):
        """Call cancel in current state."""
        Cancel(self.session, self.stdout).apply(self.cond_rm_quotes('cancel', raw))

    def do_external(self, raw):
        """Call cancel in current state."""
        External(self.session, self.stdout).apply(self.cond_rm_quotes('external', raw))

    def do_release(self, raw):
        """Call release in current state."""
        Release(self.session, self.stdout).apply(self.cond_rm_quotes('release', raw))

    def do_define(self, raw):
        """Call define in current state."""
        Define(self.session, self.stdout).apply(self.cond_rm_quotes('define', raw))

    def do_definedyn(self, raw):
        """Call definedyn in current state."""
        DefineDyn(self.session, self.stdout).apply(self.cond_rm_quotes('definedyn', raw))

    def do_filter(self, raw):
        """Call filter in current state."""
        Filter(self.session, self.stdout).apply(self.cond_rm_quotes('filter', raw))


    #
    # Queries
    #
    def do_query(self, raw):
        """Call query in current state."""
        Query(self.session, self.stdout).apply(self.cond_rm_quotes('query', raw))


def main():
    """Main routine."""
    parser = argparse.ArgumentParser(prog=release.name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('encoding', nargs='*', help='Optional encoding(s) to load', default=[])
    parser.add_argument('-c', '--const', type=str, help='Set constant value <id>=<term>')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug output')
    parser.add_argument('-e', '--enum_mode', type=str, help='Enum mode', default='auto')
    parser.add_argument('-n', '--nmodels', type=int, help='Compute at most <nmodels> models (0 for all)', default=1)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(release.__version__))
    args = parser.parse_args()
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.argv = [sys.argv[0]] # flushed cl pars such that cmd2 doesn't use them

    queryasp.aux.DEBUG = args.debug

    solve_opts = ['-n', '{0}'.format(args.nmodels),
                  '-e', '{0}'.format(args.enum_mode)]
    if args.const:
        solve_opts.extend(['-c', '{0}'.format(args.const)])
    prompt = CmdLineApp(args.encoding, solve_opts)
    prompt.cmdloop()


if __name__ == '__main__':
    sys.exit(main())
