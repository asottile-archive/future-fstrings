import distutils
import os.path

from setuptools import setup
from setuptools.command.install import install as _install


PTH = (
    'try:\n'
    '    import future_fstrings\n'
    'except ImportError:\n'
    '    pass\n'
    'else:\n'
    '    future_fstrings.register()\n'
)


class install(_install):
    def initialize_options(self):
        _install.initialize_options(self)
        # Use this prefix to get loaded as early as possible
        name = 'aaaaa_' + self.distribution.metadata.name

        contents = 'import sys; exec({!r})\n'.format(PTH)
        self.extra_path = (name, contents)

    def finalize_options(self):
        _install.finalize_options(self)

        install_suffix = os.path.relpath(
            self.install_lib, self.install_libbase,
        )
        if install_suffix == '.':
            distutils.log.info('skipping install of .pth during easy-install')
        elif install_suffix == self.extra_path[1]:
            self.install_lib = self.install_libbase
            distutils.log.info(
                "will install .pth to '%s.pth'",
                os.path.join(self.install_lib, self.extra_path[0]),
            )
        else:
            raise AssertionError(
                'unexpected install_suffix',
                self.install_lib, self.install_libbase, install_suffix,
            )


setup(cmdclass={'install': install})
