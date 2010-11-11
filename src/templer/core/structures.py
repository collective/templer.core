import sys
import os

from paste.script import copydir

class Structure(object):
    
    # Subclasses must define:
    # _structure_dir (or structure_dir())
    use_cheetah = True
    template_renderer = None
    
    def module_dir(self):
        """Returns the module directory of this template."""
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    def structure_dir(self):
        assert self._structure_dir is not None, (
            "Structure %r didn't set _structure_dir" % self)
        if isinstance( self._structure_dir, tuple):
            return self._structure_dir
        else:
            return [os.path.join(self.module_dir(), self._structure_dir),]
    
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


class BootstrapStructure(Structure):
    
    _structure_dir = 'structures/bootstrap'


class EggDocsStructure(Structure):
    
    _structure_dir = 'structures/egg_docs'