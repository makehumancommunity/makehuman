#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Backwards compatibility with older MakeHuman releases.
"""

import log
import progress

def _parse_version(version_str):
    version_str = version_str.lower().strip()
    if version_str.startswith('v'):
        version_str = version_str[1:]
    version_str = version_str.split('.')
    version_str = version_str[:3]
    version = []
    for v in version_str:
        try:
            version.append(int(v))
        except:
            break
    if len(version) == 0:
        return None
    else:
        return version

class MHMLoader(object):
    def loadProperty(self, line_data, default_load_callback):
        raise NotImplementedError("An MHM backward-compatibility loader must implement loadProperty()")

    def getAcceptedVersion(self):
        """Return the version of MHM file that this loader supports. Not mentioned
        tokens are considered as wildcards. eg. if this return [1, 0], signifying
        that it supports v1.0 MHM files, it puts a wildcard on the final token:
        all v1.0.x files, with x any number, are accepted by this loader.
        The returned version is expected to be a tuple of integers.
        """
        raise NotImplementedError("An MHM backward-compatibility loader must implement getAcceptedVersion()")

class MHM10Loader(object):
    """Provides backward compatibility with .mhm files saved with
    MakeHuman 1.0.x (release) versions.
    MH 1.0 save files are translated into a format that the current version
    understands.
    There are no guarantees that custom targets can be loaded. Also some proxies
    from the previous versions have disappeared, these will no longer load.
    """
    trail_tokens = {  "skinny-fat": "skinny|fat",
                      "more-less": "more|less",
                      "less-more": "less|more",
                      "in-out": "in|out",
                      "out-in": "out|in",
                      "down-up": "down|up",
                      "up-down": "up|down",
                      "forward-backward": "forward|backward",
                      "backward-forward": "backward|forward",
                      "min-max": "min|max",
                      "max-min": "max|min",
                      "small-big": "small|big",
                      "big-small": "big|small",
                      "incr-decr": "incr|decr",
                      "decr-incr": "decr|incr",
                      "compress-uncompress": "compress|uncompress",
                      "convex-concave": "convex|concave",
                      "moregreek-lessgreek": "moregreek|lessgreek",
                      "morehump-lesshump": "morehump|lesshump",
                      "potato-point": "potato|point",
                      "deflate-inflate": "deflate|inflate",
                      "increase-decrease": "increase|decrease",
                      "pointed-triangle": "pointed|triangle",
                      "square-round": "square|round",
                      "varun-valgus": "varun|valgus"
                   }

    leading_tokens = {  "l-eye": "eyes",
                        "r-eye": "eyes",
                        "l-ear": "ears",
                        "r-ear": "ears",
                        "l-cheek": "cheek",
                        "r-cheek": "cheek",
                        "bulge": "pelvis",
                        "l-hand": "armslegs",
                        "r-hand": "armslegs",
                        "l-foot": "armslegs",
                        "r-foot": "armslegs",
                        "l-upperarm": "armslegs",
                        "r-upperarm": "armslegs",
                        "l-lowerarm": "armslegs",
                        "r-lowerarm": "armslegs",
                        "l-leg": "armslegs",
                        "r-leg": "armslegs",
                        "l-lowerleg": "armslegs",
                        "r-lowerleg": "armslegs",
                        "l-upperleg": "armslegs",
                        "r-upperleg": "armslegs",
                        "penis": "genitals"
                     }

    modifier_mapping = {  "face": {
                          },
                          "torso": {
                          },
                          "armslegs": {
                          },
                          "gendered": {
                              "BreastSize": "breast/BreastSize",
                              "BreastFirmness": "breast/BreastFirmness",
                          },
                          "macro": {
                              "Gender": "macrodetails/Gender",
                              "Age": "macrodetails/Age",
                              "Muscle": "macrodetails-universal/Muscle",
                              "Weight": "macrodetails-universal/Weight",
                              "Height": "macrodetails-height/Height",
                              "BodyProportions": "macrodetails-proportions/BodyProportions",
                              "African": "macrodetails/African",
                              "Asian": "macrodetails/Asian",
                              "Caucasian": "macrodetails/Caucasian"
                          },
                          "measure": {
                              "bust": "measure/measure-bust-decrease|increase",
                              "neckcirc": "measure/measure-neckcirc-decrease|increase",
                              "ankle": "measure/measure-ankle-decrease|increase",
                              "napetowaist": "measure/measure-napetowaist-decrease|increase",
                              "hips": "measure/measure-hips-decrease|increase",
                              "shoulder": "measure/measure-shoulder-decrease|increase",
                              "frontchest": "measure/measure-frontchest-decrease|increase",
                              "underbust": "measure/measure-underbust-decrease|increase",
                              "neckheight": "measure/measure-neckheight-decrease|increase",
                              "lowerlegheight": "measure/measure-lowerlegheight-decrease|increase",
                              "waisttohip": "measure/measure-waisttohip-decrease|increase",
                              "waist": "measure/measure-waist-decrease|increase",
                              "wrist": "measure/measure-wrist-decrease|increase",
                              "calf": "measure/measure-calf-decrease|increase",
                              "upperarm": "measure/measure-upperarm-decrease|increase",
                              "thighcirc": "measure/measure-thighcirc-decrease|increase",
                              "lowerarmlenght": "measure/measure-lowerarmlenght-decrease|increase",
                              "upperarmlenght": "measure/measure-upperarmlenght-decrease|increase",
                              "upperlegheight": "measure/measure-upperlegheight-decrease|increase"
                          },
                          "custom": {
                          }
                       }
    skel_mapping = {  "basic.json": "default.mhskel",
                      "makehuman.json": "default.mhskel",
                      "game.json": "cmu_mb.mhskel",
                      "humanik.json": "motionbuilder_rig.mhskel",
                      "second_life.json": "opensim.mhskel",
                      "second_life_bones.json": "opensim.mhskel",
                      "xonotic.json": None,
                      "muscles.json": None
                   }

    proxy_mapping = {  "genitals": {
                            "3b354e4f-ebdb-4336-a5fb-add41fc05f12": "ece8ae91-d8d7-4e98-a737-dd1f5f08519a",  # penis proxy, replace with male genitals proxy
                            "a52a556f-076d-4f46-a3a3-931b28ff1af4": "e71e3025-e6b5-415b-87a9-92be4642c7cc",  # Vagina proxy, replace with female genitals proxy
                        }
                    }

    def loadProperty(self, line_data, default_load_callback, strict):
        prop = line_data[0]
        if prop in ['tags', 'camera', 'subdivide']:
            default_load_callback(line_data)
            return
        if prop == 'skeleton':
            skeltype = line_data[1]
            if skeltype in self.skel_mapping:
                skel = self.skel_mapping[skeltype]
                if skel:
                    default_load_callback(["skeleton", skel])
                else:
                    log.warning("There is no good replacement for MH v1.0 rig %s" % skeltype)
        elif prop in self.modifier_mapping.keys():
            mapping = self.modifier_mapping[prop]
            target_name = line_data[1]
            value = float(line_data[2])

            if prop == "custom":
                modifier_name = "custom/%s" % target_name
                default_load_callback(["modifier", modifier_name, value])
                return
            if target_name in mapping:
                default_load_callback(["modifier", mapping[target_name], value])
                return

            tokens = target_name.split('-')
            if '-'.join(tokens[-2:]) in self.trail_tokens:
                target_name = '-'.join(tokens[:-2]+[self.trail_tokens['-'.join(tokens[-2:])]])

            if tokens[0] in self.leading_tokens:
                modifier_name = "%s/%s" % (self.leading_tokens[tokens[0]], target_name)
            elif '-'.join(tokens[:2]) in self.leading_tokens:
                modifier_name = "%s/%s" % (self.leading_tokens['-'.join(tokens[:2])], target_name)
            else:
                modifier_name = "%s/%s" % (tokens[0], target_name)

            default_load_callback(["modifier", modifier_name, value])
        else:
            default_load_callback(line_data)

    def getAcceptedVersion(self):
        return (1, 0)

def getMHMLoader(version):
    for loader in mhm_loaders:
        if all([(i < len(version) and v == version[i]) for i, v in enumerate(loader.getAcceptedVersion())]):
            return loader
    raise RuntimeError("No suitable MHM backward compatibility loader found for version %s" % (version, ))

def loadMHM(version, lines, default_load_callback, strict=False):
    version_ = _parse_version(version)
    if version_ is None:
        raise RuntimeError("Failed to parse version %s" % version)

    fprog = progress.Progress(len(lines))
    loader = getMHMLoader(version_)
    for lineData in lines:
        lineData = lineData.strip().split()
        loader.loadProperty(lineData, default_load_callback, strict)
        fprog.step()


mhm_loaders = [ MHM10Loader() ]

