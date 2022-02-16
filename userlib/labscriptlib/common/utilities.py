# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 10:49:56 2022

@author: rubidium
"""

import labscript as ls

def stage(func):
    """A decorator for functions that represent stages of the experiment.
    
    Assumes first argument to function is the stage's start time, and return value is
    its duration (which is a convention we normally follow throughout labscript).
    
    If the function is passed a kwarg "stage_label" than this is used instead of the name
    of the function.
    
    The resulting decorated function simply prints the name of the stage and its start and end
    times when the function is called."""
    import functools

    @functools.wraps(func)
    def f(t, *args, **kwargs):
        duration = func(t, *args, **kwargs)
        
        label = func.__name__
        if 'stage_label' in kwargs:
            label = label + '(' + kwargs['stage_label']+')'

        try:
            float(duration)
        except Exception:
            raise TypeError("Stage function %s must return its duration, even if zero"%func.__name__)
        
        ls.add_time_marker(t, label=label, verbose=True)
        return duration
    return f