# -*- coding: utf-8 -*-
import abc


class PulloverError(Exception):
    """
    The base class of all errors raised by Pullover.
    """
    __metaclass__ = abc.ABCMeta
