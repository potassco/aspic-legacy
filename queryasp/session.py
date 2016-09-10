# -*- coding: utf-8 -*-
"""User session and states"""

from __future__ import print_function
from abc import abstractmethod
import sys
from queryasp.singletonabc import Singleton, SingletonABCMeta
from collections import Mapping
from importlib import import_module
import clingo
from queryasp.aux import debug


class State(object):
    """Represents current system state,i.e., tuple (R,I,i,j).!

    Program R (as well as I and i) are here represented as (part of) the
    clingo.Control object.

    """
    def __init__(self, prg=None, assumptions=None, ident=0):
        """Initialize State object.

        Arguments:
        prg         -- clingo.Control object (default clingo.Control())
        assumptions -- list of assumed literals (default None)
        ident       -- state identifier

        Note, that (somewhat different to the formal definition of an
        interpreter state), assertions, i.e., asserted literals and externals,
        i.e, external atoms defined in prg are not explicitly passed as
        arguments, since both are already contained by prg.

        """
        self.prg = prg or clingo.Control()
        self.assumptions = assumptions or [] # list of tuples (atom, sign)
        assert isinstance(ident, int), 'Session.__init__: wrong identifier argument!'
        self.ident = ident


class Session(object):
    """Represent a user session from start to finish.

    Provides an context for all the states and operations of a user
    session.

    """
    __metaclass__ = Singleton

    DEFAULT_CMD_MODULES = ['queryasp.scops', 'queryasp.queries', 'queryasp.auxops']
    __DEFAULT_CMD_MODULES = DEFAULT_CMD_MODULES

    @staticmethod
    def collect_cmodule_specs(module_names):
        """Method to generate module specs."""
        spec = {}
        for module_name in module_names:
            module = import_module(module_name)
            spec[module_name] = module.SPEC
        return spec

    def __init__(self, stdout=sys.stdout, prg_files=None, solve_opts=None,
                 cmd_modules=None, cmd_confs=None, cmd_shared_data=None, **kwargs):
        """Initialize Session object.

        Based on the provided program file prg_file the initial state
        is created for the session to begin

        Arguments:
        stdout               -- standard output stream used by session
        prg_files            -- optional list of program file names to be used as initial rule set (default None)
        solve_options        -- optional list of solve options for clingo (default None)
        cmd_modules          -- optional list of custom command modules (default None)
        cmd_confs            -- optional dict of custom initialization parameters for commands(default None)
        cmd_shared_data      -- optional dict of custom initial shared data for commands (default None)

        """
        self._initial_prg_files = prg_files or []
        self._initial_solve_opts = solve_opts or []
        self.stdout = stdout
        self.state = self._create_initial_state()
        self.step = 0
        self.log = [(0, "init", [])]
        Command.init_shared_data(cmd_shared_data) # TODO: should be part of command registration; also move cmd shared data into reg
        self.commands = CommandRegistration(self, cmd_modules, cmd_confs).commands  # registered and thus available command objects

    def _create_initial_state(self):
        """Returns initial session state"""
        prg = clingo.Control(self._initial_solve_opts)
        for fname in self._initial_prg_files:
            prg.load(fname)
        prg.ground([("base", [])])
        return State(prg)

    def reset_state(self, prg_files=None, solve_opts=None):
        #TODO: create explicit reset and load scops command referring to this
        # Probably whole session should never be reset, only state, i.e., solver; thus, rename to state_reset
        """Resets state by creating new clingo.Control object that optionally
        also takes a new ASP program(s) and solver options as input

        Arguments:
        prg_files     -- optional list of program file names to be used as initial rule set (default [])
        solve_options -- optional list of solve options for clingo (default [])

        """
        self._initial_prg_files = prg_files or self._initial_prg_files
        self._initial_solve_opts = solve_opts or self._initial_solve_opts
        self.state = self._create_initial_state()
        debug("State reset!")
        #TODO: callbacks to/hooks for Filter, DefineDyn


class Command(object):
    """Abstract class for all user commands available during a session."""
    __metaclass__ = SingletonABCMeta

    __shared_data = dict() # persistent, shared data between commands

    _help = 'Help text missing!'

    @classmethod
    def init_shared_data(cls, shared_data):
        """Re-initialze shared data of all commands.

        Initialialzes Command.__shared_data with an optionally given dict or an
        empty dict, otherwise.

        Arguments:
        shared_data   -- optionally given dict to initialze Command.__shared_data

        """
        if shared_data:
            assert isinstance(shared_data, dict), 'Object shared_data not of type dict!'
            Command.__shared_data = shared_data
        else:
            Command.__shared_data = dict()

    @staticmethod
    def _init_data(mapping):
        """Init data exclusive to command."""
        if mapping is None:
            return dict()
        else:
            assert isinstance(mapping, Mapping), 'Data object not of type Collections.Mapping!'
            return mapping

    @staticmethod
    def _register_to_shared_data(cmdkey, shared_keys_ivals):
        """Register command to shared data"""
        if shared_keys_ivals is None or []:
            return None
        shared = Command.__shared_data
        shared_with_key = {}
        for skey, initval in shared_keys_ivals.items():
            if not shared.has_key(skey):
                shared[skey] = (initval, [cmdkey]) # shared dict and keys of commands accessing it
            else:
                shared[skey][1].append(cmdkey) # add command to access list
            shared_with_key[skey] = shared[skey][0]
        return shared_with_key

    def __init__(self, session, stdout, **kwargs):
        """Inits Command

        Arguments:
        session -- Session object to register to
        stdout  -- stdout stream to use
        kwargs  -- optional config pars

        """
        self._session = session
        self._stdout = stdout
        self.name = kwargs.get('name') or self.__class__.__name__.lower() # unique string name used on command line and as id
        self.printer = kwargs.get('printer') or CommandPrinter('default', self)
        self.prnt = self.printer.prnt
        self._data = Command._init_data(kwargs.get('local_data'))# data exclusively accessed (r,w) by the command
        self._shared_data = Command._register_to_shared_data(self.name, kwargs.get('share_keys'))
        self.help = Command._help
        self.frontend_conf = (kwargs.get('frontend') or # defines call-back function and config attributes to be used by frontends
                              {'cmd2': {'callback': lambda raw: self.apply(raw),
                                        'multiline': False}})

    @abstractmethod
    def apply(self, raw, *args, **kwargs):
        """Abstract command application using raw input."""

    def _update_session_log(self, op_type, input_type, input_args):
        """Update session log after operator application."""
        self._session.step += 1
        self._session.log.append((self._session.step, op_type, input_type, input_args))
        debug(str(self._session.log))


class CommandPrinter(object):
    """Plugable output printer for Command output.

    By default transparent, should be extended as required by command/user requirements.
    """

    def __init__(self, mode='default', command=None):
        """__init__ method

        Arguments:
        mode    -- default print mode
        command -- command owning this printer object
        """
        self.command = command  # command owning the printer
        self.mode = mode        # selected mode

    def prnt(self, out_data=None, temp_mode=None):
        """Output printing with mode-dependent formatting.

        Only default method supported here.

        Arguments:
        out_data  -- data to be printed, expected type depending on printer and mode
        temp_mode -- optional different printing mode from self.smode to use for this print out
        """
        try:
            prnt = getattr(self, 'prnt_{0}'.format(temp_mode or self.mode)) # use temp_mode method if requested
        except AttributeError:
            print('CommandPrinter:prnt: Unknown print mode!')
        else:
            debug('Command {0} invokes print method {1} in next line:'.format(self.command, prnt))
            prnt(out_data)

    def prnt_default(self, out_data=''):
        """Transparent print method for default mode"""
        print(out_data)


class CommandRegistration(object):
    """Collects Command configs from given modules and, based on that, initializes and
    'registers' Command objects in a dict.

    Utilized by Session to
    - Collect Command configs provided by modules, i.e., the Command sub-classes and custom
      initialization parameters specified there
    - Initialize Commands with init pars

    """
    def __init__(self, session, module_names=None, cmd_confs=None):
        """Init.

        Arguments:
        module_names -- list of modules containing Commands and custom Command init pars
        cmd_confs    -- complementary, custom init pars for Commands not provided by a module

        """
        self.session = session
        self.commands = {} # Command registry, i.e., dict over pairs of the form <command_name> : <command_object>
        self._register_command_modules(session.DEFAULT_CMD_MODULES + (module_names or []), # default + custom modules
                                       cmd_confs or {})

    @staticmethod
    def _collect_cmodule_specs(module_names):
        """Method to generate module specs."""
        commands = {}
        command_confs = {}
        for module_name in module_names:
            module = import_module(module_name)
            if hasattr(module, 'COMMANDS'):
                commands[module_name] = module.COMMANDS # Commands defined in this module
                command_confs.update(dict.fromkeys(["{0}.{1}".format(module_name, class_name) for class_name in module.COMMANDS],
                                                   None)) # 1.) Pad all its Commands with default init pars, i.e., None
            else:
                raise ValueError('Module {0} does not contain COMMANDS as an attribute.'.format(module))
            if hasattr(module, 'COMMAND_CONFS'):
                command_confs.update(module.COMMAND_CONFS) # 2.) Add custom init pars if specified
        return commands, command_confs

    def _register_command_modules(self, module_names=None, cmd_confs=None):
        """Registers commands at the session's initialization"""
        commands, command_confs = CommandRegistration._collect_cmodule_specs(module_names or [])
        command_confs.update(cmd_confs or {}) # add complementary init pars if present
        for module_name in module_names:
            for class_name in commands[module_name]:
                self._register_command(module_name, class_name,
                                       command_confs["{0}.{1}".format(module_name, class_name)])

    def _register_command(self, module_name, class_name, command_conf):
        """Registers single command specified by its module and class name"""
        module = import_module(module_name)
        class_ = getattr(module, class_name)
        cmd = class_(self.session, self.session.stdout, **(command_conf or dict()))
        if self.commands.has_key(cmd.name):
            raise ValueError('Tried to add command with duplicate name to session!')
        else:
            self.commands[cmd.name] = cmd
