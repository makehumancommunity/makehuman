#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman 3D Transformation functions.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Marc Flerackers, Jonas Hauquier

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

This module contains algorithms used to perform high-level 3D
transformations on the 3D mesh that is used to represent the human
figure in the MakeHuman application.

These currently include:

  - morphing for anatomical variations
  - pose deformations
  - mesh coherency tests (for use during the development cycle)
  - visualisation functions (for use during the development cycle)

This will also be where any future mesh transformation
algorithms will be coded. For example:

  - collision deformations
  - etc..

"""

__docformat__ = 'restructuredtext'

import os
import numpy as np
import log
from getpath import getSysDataPath, canonicalPath

_targetBuffer = {}


class Target(object):
    """
    This class is used to store morph targets.
    """

    dtype = [('index','u4'),('vector','(3,)f4')]
    npzfile = None
    npztime = None
    npzdir = None

    def __init__(self, obj, name):
        """
        This method initializes an instance of the Target class.

        Parameters
        ----------

        obj:
            *3d object*. The base object (to which a target can be applied).
            This object is read to determine the number of vertices to
            use when initializing this data structure.

        name:
            *string*. The name of this target.


        """
        self.name = name
        self.morphFactor = -1

        try:
            self._load(self.name)
        except Exception as e:
            self.verts = []
            log.error('Unable to open %s (%s)', name, e)
            return

        self.faces = obj.getFacesForVertices(self.verts)

    def __repr__(self):
        return ( "<Target %s>" % (os.path.basename(self.name)) )

    @property
    def license(self):
        if hasattr(self, '_license'):
            return self._license
        elif Target.npzfile is not None and 'targets/targets.license' in Target.npzfile:
            license = defaultTargetLicense()
            return license.fromNumpyString(Target.npzfile['targets/targets.license'])
        else:
            return defaultTargetLicense()

    def setLicense(self, license):
        self._license = license

    def _load_text(self, name):
        import makehuman
        data = []
        license = defaultTargetLicense()
        with open(name, 'rU') as fd:
            for line in fd:
                line = line.strip()
                if line.startswith('#'):
                    license.updateFromComment(line)
                    continue
                translationData = line.split()
                if len(translationData) != 4:
                    continue
                vertIndex = int(translationData[0])
                translationVector = (float(translationData[1]), float(translationData[2]), float(translationData[3]))
                data.append((vertIndex, translationVector))

        raw = np.asarray(data, dtype=Target.dtype)
        self.verts = raw['index']
        self.data = raw['vector']
        if license.isCustomized():
            self.setLicense(license)

    def _load_binary_archive(self, name):
        """
        Load target from npz archive (containing multiple targets)
        """
        name = name.replace('\\', '/')
        bname = os.path.splitext(name)[0]
        iname = '%s.index' % bname
        vname = '%s.vector' % bname
        lname = '%s.license' % bname
        if os.path.isfile(name) and Target.npztime < os.path.getmtime(name):
            log.message('compiled file newer than archive: %s', name)
            raise RuntimeError('compiled file newer than archive: %s' % name)
        if iname not in Target.npzfile:
            log.message('compiled file missing: %s', iname)
            raise RuntimeError('compiled file missing: %s' % iname)
        if vname not in Target.npzfile:
            log.message('compiled file missing: %s', vname)
            raise RuntimeError('compiled file missing: %s' % vname)
        self.verts = Target.npzfile[iname]
        self.data = Target.npzfile[vname] * 1e-3
        if lname in Target.npzfile:
            import makehuman
            self._license = defaultTargetLicense().fromNumpyString(Target.npzfile[lname])

    def _load_binary_files(self, name):
        """
        Load target from individual .bin file
        """
        # TODO no longer used, to be removed
        bname = os.path.splitext(name)[0]
        iname = '%s.index.npy' % bname
        vname = '%s.vector.npy' % bname
        if not os.path.exists(iname):
            log.message('compiled file missing: %s', name)
            raise RuntimeError()
        if not os.path.exists(vname):
            log.message('compiled file missing: %s', name)
            raise RuntimeError()
        if os.path.isfile(name) and os.path.getmtime(iname) < os.path.getmtime(name):
            log.message('compiled file out of date: %s', iname)
            raise RuntimeError()
        if os.path.getmtime(vname) < os.path.getmtime(name):
            log.message('compiled file out of date: %s', vname)
            raise RuntimeError()
        self.verts = np.load(iname)
        self.data = np.load(vname) * 1e-3

    def _load_binary(self, name):
        if Target.npzfile is None:
            try:
                npzname = getSysDataPath('targets.npz')     # TODO duplicate path literal
                Target.npzdir = os.path.dirname(npzname)
                Target.npzfile = np.load(npzname)
                Target.npztime = os.path.getmtime(npzname)
            except:
                log.message('no compressed targets found')
                Target.npzfile = False
        if Target.npzfile == False:
            # Fallback to old .bin files per target     # TODO remove this
            self._load_binary_files(name)
        else:
            # Load target from npz archive
            name = os.path.relpath(name, Target.npzdir)
            self._load_binary_archive(name)

    def _save_binary(self, name):
        log.message('compiling %s', name)
        try:
            bname, ext = os.path.splitext(name)
            iname = '%s.index.npy' % bname
            vname = '%s.vector.npy' % bname
            index = np.ascontiguousarray(self.verts, dtype=np.uint16)
            vector = np.ascontiguousarray(np.round(self.data * 1e3), dtype=np.int16)
            np.save(iname, index)
            np.save(vname, vector)
            if hasattr(self, '_license'):
                lname = '%s.license.npy' % bname
                license = np.ascontiguousarray(self._license.toNumpyString())
                np.save(lname, license)
                return iname, vname, lname
            return iname, vname, None
        except StandardError, _:
            log.error('error saving %s', name)

    def _load(self, name):
        logger = log.getLogger('mh.load')
        logger.debug('loading target %s', name)
        try:
            self._load_binary(name)
        except StandardError, _:
            self._load_text(name)
        logger.debug('loaded target %s', name)

    def apply(self, obj, morphFactor, update=True, calcNormals=True, faceGroupToUpdateName=None, scale=(1.0,1.0,1.0), animatedMesh=None):
        self.morphFactor = morphFactor

        if len(self.verts):

            if morphFactor or calcNormals or update:

                if faceGroupToUpdateName:
                    # if a facegroup is provided, apply it ONLY to the verts used
                    # by the specified facegroup.
                    vmask, fmask = obj.getVertexAndFaceMasksForGroups([faceGroupToUpdateName])

                    srcVerts = np.argwhere(vmask[self.verts])[...,0]
                    facesToRecalculate = self.faces[fmask[self.faces]]
                else:
                    # if a vertgroup is not provided, all verts affected by
                    # the targets will be modified

                    facesToRecalculate = self.faces
                    srcVerts = np.s_[...]

                dstVerts = self.verts[srcVerts]

            if morphFactor:
                # Adding the translation vector

                scale = np.array(scale) * morphFactor
                if animatedMesh is not None:
                    # Pose the direction in which the target is applied, for fast
                    # approximate modeling of a posed model
                    import animation
                    vertBoneMapping = animatedMesh.getBoundMesh(obj.name)[1]
                    if not vertBoneMapping.isCompiled(4):
                        vertBoneMapping.compileData(animatedMesh.getBaseSkeleton(), 4)
                    animationTrack = animatedMesh.getActiveAnimation()
                    if not animationTrack.isBaked():
                        animationTrack.bake(animatedMesh.getBaseSkeleton())
                    poseData = animatedMesh.getPoseState()
                    obj.coord[dstVerts] += animation.skinMesh( \
                                  self.data[srcVerts] * scale[None,:], 
                                  vertBoneMapping.compiled(4)[dstVerts], poseData )
                else:
                    obj.coord[dstVerts] += self.data[srcVerts] * scale[None,:]
                obj.markCoords(dstVerts, coor=True)

            if calcNormals:
                obj.calcNormals(1, 1, dstVerts, facesToRecalculate)
            if update:
                obj.update()

            return True

        return False

def getTarget(obj, targetPath):
    """
    This function retrieves a set of translation vectors from a morphing
    target file and stores them in a buffer. It is usually only called if
    the translation vectors from this file have not yet been buffered during
    the current session.

    The translation target files contain lists of vertex indices and corresponding
    3D translation vectors. The buffer is structured as a list of lists
    (a dictionary of dictionaries) indexed using the morph target file name, so:
    \"targetBuffer[targetPath] = targetData\" and targetData is a list of vectors
    keyed on their vertex indices.

    For example, a translation direction vector
    of [0,5.67,2.34] for vertex 345 would be stored using
    \"targetData[345] = [0,5.67,2.34]\".
    If this is taken from target file \"foo.target\", then this targetData could be
    assigned to the buffer with 'targetBuffer[\"c:/MH/foo.target\"] = targetData'.

    Parameters
    ----------

    obj:
        *3d object*. The target object to which the translations are to be applied.
        This object is read by this function to define a list of the vertices
        affected by this morph target file.

    targetPath:
        *string*. The file system path to the file containing the morphing targets.
        The precise format of this string will be operating system dependant.
    """
    targetPath = canonicalPath(targetPath)

    try:
        return _targetBuffer[targetPath]
    except KeyError:
        pass

    target = Target(obj, targetPath)
    _targetBuffer[targetPath] = target
    return target

def refreshCachedTarget(targetPath):
    """
    Invalidate the cache for the specified target, so that it will be reloaded
    next time it is requested.
    Generally this only has effect if the target was loaded from an ascii file,
    not from npz archive.
    """
    targetPath = canonicalPath(targetPath)
    if targetPath in _targetBuffer:
        del _targetBuffer[targetPath]

def loadTranslationTarget(obj, targetPath, morphFactor, faceGroupToUpdateName=None, update=1, calcNorm=1, scale=[1.0,1.0,1.0], animatedMesh=None):
    """
    This function retrieves a set of translation vectors and applies those
    translations to the specified vertices of the mesh object. This set of
    translations corresponds to a particular morph target file.
    If the file has already been loaded into memory then the translation
    vectors are read from the target data buffer, otherwise a function is
    first called to load the target data from disk into a buffer for
    future use.

    The translation target files contain lists of vertex indices and corresponding
    3D translation vectors. The translation vector for each vertex is multiplied
    by a common factor (morphFactor) before being applied to the specified vertex.

    Parameters
    ----------

    obj:
        *3d object*. The target object to which the translations are to be applied.
        This object is read and updated by this function.

    targetPath:
        *string*. The file system path to the file containing the morphing targets.
        The precise format of this string will be operating system dependant.

    morphFactor:
        *float*. A factor between 0 and 1 controlling the proportion of the translations
        to be applied. If 0 then the object remains unmodified. If 1 the 'full' translations
        are applied. This parameter would normally be in the range 0-1 but can be greater
        than 1 or less than 0 when used to produce extreme deformations (deformations
        that extend beyond those modelled by the original artist).

    faceGroupToUpdateName:
        *string*. Optional: The name of a single facegroup to be affected by the target.
        If specified, then only transformations to faces contained by the specified
        facegroup are applied. If not specified, all transformations contained within the
        morph target file are applied. This permits a single morph target file to contain
        transformations that affect multiple facegroups, but to only be selectively applied
        to individual facegroups.

    update:
        *int flag*. A flag to indicate whether the update method on the object should be called.

    calcNorm:
        *int flag*. A flag to indicate whether the normals are to be recalculated (1/true)
        or not (0/false).

    scale:
        *float*. Scale the target offsets with this vector. Defaults to unit vector.

    animatedMesh:
        *AnimatedMesh*. Posed state of the basemesh with which the target should 
        be transformed before being applied.

    """

    if not (morphFactor or update):
        return

    target = getTarget(obj, targetPath)

    target.apply(obj, morphFactor, update, calcNorm, faceGroupToUpdateName, scale, animatedMesh)

def saveTranslationTarget(obj, targetPath, groupToSave=None, epsilon=0.001):
    """
    This function analyses an object to determine the differences between the current
    set of vertices and the vertices contained in the *originalVerts* list, writing the
    differences out to disk as a morphing target file.

    Parameters
    ----------

    obj:
        *3d object*. The object from which the current set of vertices is to be determined.

    targetPath:
        *string*. The file system path to the output file into which the morphing targets
        will be written.

    groupToSave:
        *faceGroup*. It's possible to save only the changes made to a specific part of the
        mesh object by indicating the face group to save.

    epsilon:
        *float*. The distance that a vertex has to have been moved for it to be
        considered 'moved'
        by this function. The difference between the original vertex position and
        the current vertex position is compared to this value. If that difference is greater
        than the value of epsilon, the vertex is considered to have been modified and will be
        saved in the output file as a morph target.

    """

    if not groupToSave:
        vertsToSave = np.arange(len(obj.coord))
    else:
        pass  # TODO verts from group

    originalVerts = obj.orig_coord[vertsToSave]
    targetVerts = obj.coord[vertsToSave]

    delta = targetVerts - originalVerts
    dist2 = np.sum(delta ** 2, axis=-1)
    valid = dist2 > (epsilon ** 2)
    del dist2
    delta = delta[valid]
    vertsToSave = vertsToSave[valid]
    nVertsExported = len(vertsToSave)

    try:
        with open(targetPath, 'w') as fileDescriptor:
            for i in xrange(nVertsExported):
                fileDescriptor.write('%d %f %f %f\n' % (vertsToSave[i], delta[i,0], delta[i,1], delta[i,2]))

        if nVertsExported == 0:
            log.warning('Zero verts exported in file %s', targetPath)
    except Exception as e:
        log.error('Unable to open %s (%s)', targetPath, e)
        return None


def resetObj(obj, update=None, calcNorm=None):
    """
    This function resets the positions of the vertices of an object to their original base positions.

    Parameters
    ----------

    obj:
        *3D object*. The object whose vertices are to be reset.

    update:
        *int*. An indicator to control whether to call the vectors update method.

    calcNorm:
        *int*. An indicator to control whether or not the normals should be recalculated

    """

    originalVerts = obj.orig_coord
    obj.changeCoords(originalVerts)
    if update:
        obj.update()
    if calcNorm:
        obj.calcNormals()

def defaultTargetLicense():
    """
    Default license for targets, shared for all targets that do not specify
    their own custom license, which is useful for saving storage space as this
    license is globally referenced by and applies to the majority of targets.
    """
    import makehuman
    return makehuman.getAssetLicense( {"license": "AGPL3",
                                       "author": "MakeHuman",
                                       "copyright": "2016 Data Collection AB, Joel Palmius, Jonas Hauquier"} )
