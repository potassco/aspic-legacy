# -*- coding: utf-8 -*-
"""Frontend Factories"""

from __future__ import print_function
from abc import ABCMeta, abstractmethod
from queryasp.session import Session
from queryasp.aux import debug, on_model
from queryasp import release
import cmd2

class FrontendFactory(object):
    """Abstract FrontendFactory.

    """

    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def newFrontend(session):
        pass

    @staticmethod
    @abstractmethod
    def runFrontend(frontend_obj):
        pass

class Cmd2Factory(FrontendFactory):
    """Cmd2 front-end factory.

    """
    @staticmethod
    def newFrontend(session):
        for cmd_name, cmd_object in session.commands.items():
            Cmd2Factory._add_command(cmd_name, cmd_object)
        return Cmd2_CmdLineApp(session)

    @staticmethod
    def runFrontend(clapp_obj):
        clapp_obj.cmdloop()

    @staticmethod
    def _add_command(cmd_name, cmd_obj):
        """Adds front-end method with callback to command"""
        def do_cmd(self, raw, *args, **kwargs):
            cmd_obj.frontend_conf['cmd2']['callback'](Cmd2_CmdLineApp.cond_rm_quotes(cmd_obj, raw),
                                                      *args, **kwargs)
        def help_cmd(self):
            print(cmd_obj.help)
        setattr(Cmd2_CmdLineApp, 'do_' + cmd_name, do_cmd)     # Add commmand and...
        setattr(Cmd2_CmdLineApp, 'help_' + cmd_name, help_cmd) # its help func.
        debug(Cmd2Factory._add_command,
              "Added callback func of {1} as do_{0} method to Cmd2LineApp class.".format(cmd_name, cmd_obj))


class Cmd2_CmdLineApp(cmd2.Cmd, object):
    """Cmd2-based command line interpreter class.

    Used by Cmd2Factory as template for further customization.
    """

    #cmd2 settings
    #intro = "Welcome to ASPIC 0.1"
    prompt = "?- "
    # multilineCommands = ['define', 'definedyn']
    terminators = ['?']
    defaultExtension = 'aic'            # For ``save``, ``load``, etc.
    default_file_name = 'command.aic'   # For ``save``, ``load``, etc.

    def __init__(self, session):
        """Initialize CmdLineApp object.

        Arguments:
        prg_files     -- program file names to load (default [])
        solve_options -- solve options for clingo (default [])

        """
        print("Welcome to {0} {1}".format(release.name, release.__version__))
        super(self.__class__, self).__init__()
        self.session = session
        Cmd2_CmdLineApp.multilineCommands = [c for c in session.commands if
                                             session.commands[c].frontend_conf['cmd2']['multiline']]

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
            cmd, args = aspic_exp.split(None, 1)
            if (cmd in self.session.commands and not
                    self.session.commands[cmd].frontend_conf['cmd2']['multiline']):
                rewrite = "{0} '{1}'".format(cmd, args)
                if pipe:
                    rewrite = rewrite + '|' + pipe
                debug(rewrite, "ClApp.preparse return val")
                return rewrite
        return raw

    @staticmethod
    def cond_rm_quotes(cmd_obj, qraw):
        """Remove quotes from arguments quoted by function 'preparse'

        Arguments:
        cmd_obj -- command
        qraw    -- quoted, raw string of arguments
        """
        if not cmd_obj.frontend_conf['cmd2']['multiline']:
            return qraw[1:-1]
        else:
            return qraw

    #
    # Globally predefined shell commands
    #
    def do_exec(self, arg=None): #Renaming wrapper for Cmd2.do_load script invocation
        """Runs an aspic shell script at given path.

        Arguments:
        arg -- path to aspic script to run
        """
        super(self.__class__, self).do_load(arg)
