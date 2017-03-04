#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Definition of Sorter class.

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

This module contains the Sorter class, a utility that is useful
for keeping a collection of objects sorted accoding to a custom
method. The methods that the Sorter can use to sort objects
are stored inside the Sorter, so that they can later be
accessed in convenient ways.

"""


class Sorter(object):
    """
    The Sorter class is a utility that can be used to sort
    and generally apply ordering-based actions to lists
    of objects by using customized ordering methods.

    Ordering methods
    are functions that take an object as a parameter
    and return an orderable object that will be used as a
    sorting key.
    """

    class Methods(object):
        """
        The Sorter.Methods class is a container of ordering methods
        similar to a dictionary, but able to store the order of the
        sortable fields that are given during assignment.
        """

        def __init__(self):
            """
            Construct an empty Methods container.
            """

            self.clear()

        def fields(self):
            """
            Return the fields for which there is an ordering method
            in this Methods container. The order of the fields is
            same as the one given during the assignment of the
            Methods container's contents.

            :return: The names of the fields of the
                ordering methods in the container
            :rtype: list of strings
            """

            return self._fields

        def __contains__(self, field):
            """
            Return whether a field exists in this container.

            :rtype: bool
            """

            return field in self._methods

        def __getitem__(self, field):
            """
            Return the ordering method that is
            associated with the given field.

            :param field: Name of the field to return the ordering method for
            :type field: str

            :return: Ordering method for the given field
            :rtype: function
            """

            return self._methods[field]

        def clear(self):
            """
            Clears the contents of the container.
            """

            self._methods = {}
            self._fields = []

        def assign(self, methods):
            """
            Set the contents of the Methods container.

            :param methods: List of pairs of the new sortable fields
                and their sorting methods
            :type methods: list of tuples
            """

            self._methods = dict(methods)
            self._fields = list(zip(*methods)[0])

        def extend(self, methods):
            """
            Extend the contents of the Methods container with new methods.

            :param methods: List of pairs of the new sortable fields
                and their sorting methods
            :type methods: list of tuples
            """

            self._methods.update(methods)
            self._fields.extend(list(zip(*methods)[0]))

    def __init__(self):
        """
        Construct a new Sorter object with an empty
        container of ordering methods.
        """

        self._methods = self.Methods()

    def fields(self):
        """
        Returns the names of the fields which this Sorter can sort.

        :return: The names of the fields which this Sorter can sort.
        :rtype: list of strings
        """

        return self.methods.fields()

    def getMethods(self):
        """
        Returns the container with the ordering methods of this Sorter.

        :return: The ordering methods of the Sorter
        :rtype: Sorter.Methods
        """

        return self._methods

    def setMethods(self, methods):
        """
        Assigns new content to the Sorter's ordering methods container.

        :param methods: List of pairs of the new sortable fields
            and their sorting methods
        :type methods: list of tuples
        """

        self.methods.assign(methods)

    methods = property(getMethods, setMethods)

    def getMethod(self, field):
        """
        Get an ordering method for the given field.

        :rtype: function
        """

        return self.methods[field]

    def sort(self, by, objects):
        """
        Main sorting function.

        The Sorter will first decorate the objects in tuples
        along with their sorting key, which it will acquire
        by calling the sort key generator in Sorter.methods[by],
        and then it will sort the decorated tuples according
        to the key attached to them.
        Finally the decoration will be stripped and the
        sorted list of the objects will be returned.

        :param by: Name of the field by which the list of objects
            will be sorted.
        :type by: str

        :param objects: List of objects to be sorted
        :type objects: list

        :return: Sorted list of objects
        :rtype: list
        """

        decorated = self._getDecorated(self.getMethod(by), objects)
        return self._decoratedSort(decorated)

    @staticmethod
    def _getDecorated(keyFn, objects):
        """
        Static method that decorates the objects of a list
        to tuples containing an orderable key generated
        by applying keyFn on the objects, an index,
        and the object.

        :param keyFn: Ordering method (function that takes
            an object as parameter and returns a corresponding
            orderable key)
        :type keyFn: function

        :param objects: List of objects to be decorated
            with orderable keys
        :type objects: list

        :return: List of decorated objects
        :rtype: list of tuples
        """

        return [
            (keyFn(object), i, object)
            for i, object in enumerate(objects)]

    @staticmethod
    def _decoratedSort(toSort):
        """
        Static method that sorts a decorated list
        according to the keys found at the first
        position of the decoration tuple. It then
        removes the decoration and returns the
        raw sorted list.

        :param toSort: Decorated list to be sorted
        :type toSort: list of tuples

        :return: Sorted list of objects, with the
            decoration removed
        :rtype: list
        """

        toSort.sort()
        return [object for _, _, object in toSort]

    def insert(self, by, object, objects):
        """
        Method to insert an object in a sorted list.
        It is accomplished using binary search.
        Source: http://hg.python.org/cpython/file/2.7/Lib/bisect.py

        :param by: Name of the field by which the list of objects
            is sorted.
        :type by: str

        :param object: Object to insert in the list.
        :type object: any

        :param objects: List of objects to insert the object into.
        :type objects: list

        :return: The given list with the object inserted
        :rtype: list
        """

        lo = 0
        hi = len(objects)
        keyFn = self.getMethod(by)
        while lo < hi:
            mid = (lo + hi) // 2
            if keyFn(objects[mid]) < keyFn(object): lo = mid + 1
            else: hi = mid
        objects.insert(lo, object)
        return objects

    def __getattr__(self, attr):
        """
        The getattr method of the Sorter is overriden to convert
        Sorter.sortField(objects) to Sorter.sort(field, objects).

        Example:
            FileSort.sortName(filenames)
        is equivalent to:
            FileSort.sort('name', filenames)
        """

        if attr != 'sort' and attr.startswith('sort'):
            field = attr[4:].lower()
            return lambda objects: self.sort(field, objects)
        else:
            return super(Sorter, self).__getattr__(attr)
