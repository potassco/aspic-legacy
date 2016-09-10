#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ASPIC - Main Routine"""

from __future__ import print_function
import os
import argparse
import sys
from queryasp.session import Session
from queryasp.frontend import Cmd2Factory
import queryasp.aux
from queryasp import release

def main():
    """Main routine."""
    parser = argparse.ArgumentParser(prog=release.name,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     add_help=False)
    # General options
    basic_args = parser.add_argument_group('basic options')
    basic_args.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    basic_args.add_argument('-v', '--version', action='version',
                            version='%(prog)s {0}'.format(release.__version__))
    basic_args.add_argument('-d', '--debug', action='store_true', help='Debug output')
    basic_args.add_argument('encoding', nargs='*',
                            help='Optional encoding file to load', metavar='<encoding>')

    # Aspic command-specific options
    cmd_args = parser.add_argument_group('command configuration options')
    cmd_args.add_argument('-m', '--cmd_modules', nargs='+',
                          help='White-space separated list of modules with custom commands to load.',
                          default=[], metavar='<cmd_module>')
    cmd_args.add_argument('-l', '--solve-timelimit', type=int,
                          help='Set the time limit for %(prog)s\'s solve and query command invocation to %(metavar)s seconds (0 for none)',
                          default=0, metavar='<n>') #TODO cannot be directly set in clingo.Control, has to set when solving as SolveFuture.wait(<n>)

    # Clasp specific options (directly passable to the clingo.Control.config configuration proxy)
    clasp_args = parser.add_argument_group('native solver configuration options (*use with care*)')
    clasp_args.add_argument('-c', '--const', type=str,
                            help='Set the constant value %(metavar)s', metavar='<id>=<term>')
    clasp_args.add_argument('-e', '--enum-mode', type=str,
                            help='Set the enumeration algorithm to %(metavar)s',
                            default='auto', metavar='<arg>')
    clasp_args.add_argument('-n', '--nmodels', type=int,
                            help='Compute at most %(metavar)s models (0 for all)',
                            default=1, metavar='<n>')

    args = parser.parse_args()

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.argv = [sys.argv[0]] # flushed cl pars such that cmd2 doesn't use them

    queryasp.aux.DEBUG = args.debug

    solve_opts = ['-n', '{0}'.format(args.nmodels),
                  '-e', '{0}'.format(args.enum_mode)]
    if args.const:
        solve_opts.extend(['-c', '{0}'.format(args.const)])
    session = Session(None, args.encoding, solve_opts, args.cmd_modules)
    frontend = Cmd2Factory.newFrontend(session)
    Cmd2Factory.runFrontend(frontend)

if __name__ == '__main__':
    sys.exit(main())
