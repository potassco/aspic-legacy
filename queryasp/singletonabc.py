# -*- coding: utf-8 -*-
"""Singleton and SingletonABCMeta"""

from abc import ABCMeta

class Singleton(type):
    """Metaclass for defining Singleton class"""
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABCMeta(ABCMeta):
    """ABC metaclass extended by Singleton pattern"""
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonABCMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
