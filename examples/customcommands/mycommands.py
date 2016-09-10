# -*- coding: utf-8 -*-
"""Example Custom Commands"""

from __future__ import print_function
from queryasp.session import Command
from queryasp.session import CommandPrinter

# SPEC = dict.fromkeys(['Echo', 'Sum'], None)

class Echo(Command):
    """Echo command."""
    def apply(self, raw, *args, **kwargs):
        self.prnt(raw)

class Sum(Command):
    """Sum command."""
    def apply(self, raw, *args, **kwargs):
        self.prnt(str(sum([int(i) for i in raw.split()])))

class MyPrinter(CommandPrinter):

    def prnt_default(self, out_data):
        print("**MyPrinter**: " + out_data)


# Commands provided by this module
COMMANDS = ['Echo', 'Sum']

# Custom init parameters for Command sub-classes defined here or in other modules
# findable via PYTHON_PATH
COMMAND_CONFS = dict.fromkeys(['mycommands.Echo', 'queryasp.auxops.Solve'], {'printer' : MyPrinter()})
