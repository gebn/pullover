# -*- coding: utf-8 -*-
import abc


class PulloverError(Exception):
    """
    The abstract base class of all errors raised by pullover.
    """
    __metaclass__ = abc.ABCMeta
