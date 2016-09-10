# -*- coding: utf-8 -*-
"""Unit Tests for Frontend Factories"""
import sys
from queryasp.session import Session
from queryasp.frontend import Cmd2Factory

def main():
    """Main routine."""
    n = 10
    e = 'auto'
    solve_opts = ['-n', '{0}'.format(n),
                  '-e', '{0}'.format(e)]
    prg_files = None
    session = Session(None, prg_files, solve_opts, None)
    frontend = Cmd2Factory.newFrontend(session)
    Cmd2Factory.runFrontend(frontend)

if __name__ == '__main__':
    sys.exit(main())
