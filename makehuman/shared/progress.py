#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Definition of Progress class.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

The Progress module defines the Progress class, which provides
an easy interface for handling MH's progress bar.
It automatically processes porgress updates in subroutines, so
passing progress callbacks as function parameters is needless.

*-- Usage --*

from progress import Progress


# Standard usage.

def foo():
    progress = Progress()

    ... # do stuff #
    progress(0.7)
    ... # more stuff #
    progress(1.0)


# Usage in steps.

def bar():
    progress = Progress(42)

    ... # step 1 #
    progress.step()
    ... # step 2 #
    progress.step()
    ....
    ....
    ... # step 42 #
    progress.step()


# Usage in loops.

def baz(items):
    progress = Progress(len(items))

    for item in items:
        loopprog = Progress()
        ... # do stuff #
        loopprog(0.3)
        ... # more stuff #
        loopprog(0.6)
        ... # even more stuff #
        progress.step()


# All together!!!

def FooBarBaz():
    progress = Progress.begin()

    progress(0, 0.3, "Getting some foo")
    somefoo = foo()

    progress(0.3, 0.7, None)
    prog2 = Progress() (0, 0.5, "Getting a bar")
    bar1 = bar()
    prog2(0.5, 1, "Getting another bar")
    bar2 = bar()

    progress(0.7, 0.99, "Bazzing them all together")
    bazzable = [somefoo, bar1, bar2]
    baz(bazzable)

    progress(1.0, None, "Foobar bazzed.")


-----

- Weighted steps

Progress constructor can accept an iterable as the steps parameter.
In that case, the weighted step mode is activated, and steps with
greater weight in the iterable affect larger area of the progress bar.

Example:
progress = Progress([7, 3, 6, 6])

- Logging

With the logging=True option, Progress will log.debug its progress and
description for every change in its progress. (This does not include
sub-Progresses that have logging disabled.) A number of dashes is added
at the beginning of the log message representing the level of nesting
of the current procedure, to help distinguish between the messages logged
from the parent and the child Progress. With logging=False, this feature
is forced disabled. The default setting, logging=None, inherits the logging
setting from its parent (resolves to False if root progress has no logging 
enabled).

If messaging is enabled too, on a description change, Progress will log.debug
only its progress, and will let messaging to log.message the description
afterwards.

- Timing

If logging is enabled, with the timing=True option, Progress will measure
and log.debug the time each step took to complete, as well as the total time
needed for the whole procedure.

- Messaging

With the messaging=True option, Progress will log.message its description
every time it changes.
 
"""


global current_Progress_
current_Progress_ = None


class Progress(object):

    class LoggingRequest(object):
        def __init__(self, text, *args):
            self.text = text
            self.args = args
            self.level = 0
            self.withLogger('debug')

        def withLogger(self, loggerstr):
            import log
            self.logger = getattr(log, loggerstr)
            return self

        def propagate(self):
            self.level += 1

        def execute(self):
            text = self.level * '-' + self.text
            self.logger(text, *self.args)

    def __init__(self, steps=0, progressCallback=True,
            logging=None, timing=False, messaging=False):
        global current_Progress_

        self.progress = 0.0
        self.nextprog = None
        self.steps = steps
        self.stepsdone = 0
        self._description = None
        self.args = []

        self.description_changed = False

        # Weighted steps feature
        if hasattr(self.steps, '__iter__'):
            ssum = float(sum(self.steps))
            self.stepweights = [s / ssum for s in self.steps]
            self.steps = len(self.steps)
        else:
            self.stepweights = None

        self.time = None
        self.totalTime = 0.0

        self.logging = logging
        self.timing = timing
        self.messaging = messaging
        self.logging_requests = []

        # Push self in the global Progress object stack.
        self.parent = current_Progress_
        current_Progress_ = self

        # If this is a master Progress, get the callback
        # that updates MH's progress bar.
        if self.parent is None:
            if progressCallback is True:
                from core import G
                self.progressCallback = G.app.progress
            else:
                # Bypass importing if the user provided us
                # with a custom progress callback.
                self.progressCallback = progressCallback
            # To completely disable updating when this is a
            # master Progress, pass None as progressCallback.
        else:
            if self.logging is None:
                self.logging = self.parent.logging

    def getDescription(self):
        return self._description

    def setDescription(self, desc):
        self._description = desc
        self.description_changed = True

    description = property(getDescription, setDescription)

    def stepWeight(self):
        '''Internal method that returns the weight of
        the next step.'''
        if self.steps == 0:
            if self.nextprog is None:
                return 0
            else:
                return self.nextprog - self.progress
        elif self.stepweights is None:
            return 1.0 / float(self.steps)
        else:
            return self.stepweights[self.stepsdone]

    def update(self, prog=None, desc=None, args=[], is_childupdate=False):
        '''Internal method that is responsible for the
        actual progress bar updating.'''

        if prog is None:
            prog = self.progress

        if desc is None and self.description:
            desc = self.description
            args = self.args

        desc_str = "" if desc is None else desc

        if not is_childupdate:
            if self.timing:
                import time
                t = time.time()
                if self.time:
                    deltaT = (t - self.time)
                    self.totalTime += deltaT
                    if self.logging:
                        self.logging_requests.append(
                            self.LoggingRequest("  took %.4f seconds", deltaT))
                self.time = t

            if self.logging:
                if self.messaging and self.description_changed:
                    self.logging_requests.append(self.LoggingRequest(
                        self.getProgressString()))
                else:  # TODO: Format desc with args
                    self.logging_requests.append(self.LoggingRequest(
                        "%s: %s", self.getProgressString(), desc_str))

            if self.messaging and self.description_changed:
                self.logging_requests.append(self.LoggingRequest(
                    desc_str, *args).withLogger('message'))

            self.description_changed = False

        self.propagateRequests()

        if self.parent is None:
            for r in self.logging_requests: r.execute()
            self.logging_requests = []
            if self.progressCallback is not None:
                self.progressCallback(prog, desc_str, *args)

        if self.steps and self.stepsdone == self.steps or \
            self.steps == 0 and self.progress >= 0.999999:
            # Not using 1.0 for precision safety.
            self.finish()

        if self.parent:
            self.parent.childupdate(prog, desc, args)

    def propagateRequests(self):
        '''Internal method that recursively passes the logging
        requests to the master Progress.'''

        if self.parent is not None:
            for r in self.logging_requests: r.propagate()
            self.parent.logging_requests.extend(self.logging_requests)
            self.logging_requests = []
            self.parent.propagateRequests()

    def childupdate(self, prog, desc, args=[]):
        '''Internal method that a child Progress calls for doing a
        progress update by communicating with its parent.'''

        prog = self.progress + prog * self.stepWeight()

        self.update(prog, desc, args, is_childupdate=True)

    def getProgressString(self):
        if self.steps:
            return "Step %i/%i" % (self.stepsdone, self.steps)
        else:
            return "Progress %.2f%%" % (self.progress*100)

    def finish(self):
        '''Method to be called when a subroutine has finished,
        either explicitly (by the user), or implicitly
        (automatically when progress reaches 1.0).'''

        global current_Progress_

        if self.parent is None and self.logging and self.timing:
            import log
            log.debug("Total time taken: %s seconds.", self.totalTime)

        current_Progress_ = self.parent

    def __call__(self, progress, end=None, desc=False, *args):
        '''Basic method for progress updating.
        It overloads the () operator of the constructed object.
        Pass None to desc to disable the description; the parent
        will update it instead in that case.'''

        global current_Progress_
        current_Progress_ = self

        if not (desc is False):
            self.description = desc
            self.args = args

        self.progress = progress
        self.nextprog = end
        self.update()

        return self

    def step(self, desc=False, *args):
        '''Method useful for smaller tasks that take a number
        of roughly equivalent steps to complete.
        You can use this in a non-stepped Progress to just
        update the description on the status bar.'''

        global current_Progress_
        current_Progress_ = self

        if not (desc is False):
            self.description = desc
            self.args = args

        if self.steps:
            self.progress += self.stepWeight()
            self.stepsdone += 1
            if self.stepsdone == self.steps: self.progress = 1.0

        self.update()

        return self

    def firststep(self, desc=False, *args):
        '''Method to be called from Progress routines that work in
        discrete steps, to update the initial description and
        initialize the timing.'''

        global current_Progress_
        current_Progress_ = self

        if not (desc is False):
            self.description = desc
            self.args = args

        self.update()

        return self

    @classmethod
    def begin(cls, *args, **kwargs):
        '''Class method for directly creating a master Progress object.
        Resets all progress to zero. Use this for starting a greater MH task.
        The arguments are forwarded to the Progress constructor.
        '''

        global current_Progress_
        current_Progress_ = None

        return cls(*args, **kwargs)

    ## Specialized methods follow ##

    def HighFrequency(self, interval):
        '''Method that prepares the Progress object to run in a hispeed loop
        with high number of repetitions, which needs to progress the bar
        while looping without adding callback overhead.
        WARNING: ALWAYS test the overhead. Don't use this
        in extremely fast loops or it might slow them down.'''

        # Loop number interval between progress updates.
        self.HFI = interval

        # Replace original step method with the high frequency step.
        self.dostep = self.step
        self.step = self.HFstep

        return self

    def HFstep(self):
        '''Replacement method to be called in a hispeed loop instead of step().
        It is replaced internally on HighFrequency() (call step() to use it).'''

        if self.stepsdone % self.HFI > 0 and self.stepsdone < self.steps - 1:
            self.stepsdone += 1
        else:
            self.dostep()
