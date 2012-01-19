import sys
import os

from paste.script import copydir


class Structure(object):

    # Subclasses must define:
    # _structure_dir (or structure_dir())
    use_cheetah = True
    template_renderer = None
    _structure_dir = None

    def module_dir(self):
        """Returns the module directory of this template."""
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    def structure_dir(self):
        assert self._structure_dir is not None, (
            "Structure %r didn't set _structure_dir" % self)
        if isinstance(self._structure_dir, tuple):
            return self._structure_dir
        else:
            return [os.path.join(self.module_dir(), self._structure_dir), ]

    def write_files(self, command, output_dir, vars):
        structure_dirs = self.structure_dir()
        if len(structure_dirs) > 0:
            if not os.path.exists(output_dir):
                print "Creating directory %s" % output_dir
                if not command.simulate:
                    os.makedirs(output_dir)
            for structure_dir in structure_dirs:
                copydir.copy_dir(structure_dir, output_dir,
                                 vars,
                                 verbosity=0,
                                 simulate=command.options.simulate,
                                 interactive=command.interactive,
                                 overwrite=command.options.overwrite,
                                 indent=1,
                                 use_cheetah=self.use_cheetah,
                                 template_renderer=self.template_renderer)


class EggDocsStructure(Structure):
    _structure_dir = 'structures/egg_docs'


class ASLStructure(Structure):
    _structure_dir = 'structures/licenses/asl'


class BSDStructure(Structure):
    _structure_dir = 'structures/licenses/bsd'


class EFLStructure(Structure):
    _structure_dir = 'structures/licenses/efl'


class FDLStructure(Structure):
    _structure_dir = 'structures/licenses/fdl'


class GPLStructure(Structure):
    _structure_dir = 'structures/licenses/gpl2'


class GPL3Structure(Structure):
    _structure_dir = 'structures/licenses/gpl3'


class LGPLStructure(Structure):
    _structure_dir = 'structures/licenses/lgpl'


class MITStructure(Structure):
    _structure_dir = 'structures/licenses/mit'


class MPLStructure(Structure):
    _structure_dir = 'structures/licenses/mpl'


class MPL11Structure(Structure):
    _structure_dir = 'structures/licenses/mpl11'


class NPLStructure(Structure):
    _structure_dir = 'structures/licenses/npl'


class ZPLStructure(Structure):
    _structure_dir = 'structures/licenses/zpl'
