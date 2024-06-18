#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@summary: A wrapper module around the pyvmomi module to simplify work and handling.

@author: Frank Brehm
@contact: frank@brehm-online.com
@license: LGPL3+
@copyright: © 2024 Frank Brehm, Berlin
"""
from __future__ import print_function

import datetime
import glob
import os
import pprint
import re
import subprocess
import sys
import textwrap
from pathlib import Path

# own modules:
__base_dir__ = Path(os.path.abspath(os.path.dirname(__file__)))
__bin_dir__ = __base_dir__ / 'bin'
__lib_dir__ = __base_dir__ /  'lib'
__module_dir__ = __lib_dir__ / 'fb_vmware'
__init_py__ = __module_dir__ / '__init__.py'
__local_usr_dir__ = __base_dir__ / 'usr'
__share_dir__ = Path(sys.base_prefix) / 'share'
__local_share_dir__ = Path(str(__base_dir__) + str(__share_dir__)).relative_to(__base_dir__)
__man_dir__ = Path('share/man')
__local_man_dir__ = __local_share_dir__ / 'man' 
__man1_dir__ = __man_dir__ / 'man1'
__local_man1_dir__ = __local_man_dir__ / 'man1'
__locale_dir__ = Path('share/locale')
__local_locale_dir__ = __base_dir__ / 'locale'

__debian_dir__ = __base_dir__ / 'debian'
__changelog_file__ = __debian_dir__ / 'changelog'
__readme_file__ = __base_dir__ / 'README.md'

PATHS = {
    '__base_dir__': __base_dir__,
    '__bin_dir__': __bin_dir__,
    '__lib_dir__': __lib_dir__,
    '__module_dir__': __module_dir__,
    '__init_py__': __init_py__,
    '__local_usr_dir__': __local_usr_dir__,
    '__share_dir__': __share_dir__,
    '__local_share_dir__': __local_share_dir__,
    '__locale_dir__': __locale_dir__,
    '__man_dir__': __man_dir__,
    '__man1_dir__': __man1_dir__,
    '__local_man_dir__': __local_man_dir__,
    '__local_man1_dir__': __local_man1_dir__,
    '__debian_dir__': __debian_dir__,
    '__changelog_file__': __changelog_file__,
    '__readme_file__': __readme_file__,
    '__local_locale_dir__': __local_locale_dir__,
}

# -----------------------------------
def pp(obj):
    """Human friendly output of data structures."""
    pprinter = pprint.PrettyPrinter(indent=4)
    return pprinter.pformat(obj)

print("Paths:\n{}".format(pp(PATHS)))


if __module_dir__.exists() and __init_py__.is_file():
    sys.path.insert(0, str(__lib_dir__))

# Third party modules
from babel.messages import frontend as babel

# Third party modules
import fb_vmware

from setuptools import setup
from setuptools.command.sdist import sdist

# from fb_tools.common import pp

ENCODING = 'utf-8'

__packet_version__ = fb_vmware.__version__

__packet_name__ = 'fb_vmware'
__debian_pkg_name__ = 'fb-vmware'

__author__ = 'Frank Brehm'
__contact__ = 'frank@brehm-online.com'
__copyright__ = '(C) 2024 Frank Brehm, Berlin'
__license__ = 'LGPL3+'
__url__ = 'https://github.com/fbrehm/fb-vmware'


__open_args__ = {'encoding': ENCODING, 'errors': 'surrogateescape'}

# -----------------------------------
def read(file2read):
    """Read the given file and return its content."""
    content = None

    with file2read.open('r', **__open_args__) as fh:
        content = fh.read()

    return content


# -----------------------------------
def is_python_file(file2inspect):
    """Return, whether the given file seems to be a Python source file."""
    if file2inspect.suffix == '.py':
        return True
    else:
        return False

# -----------------------------------
def get_debian_version():
    """Return the latest package version fron Debian changelog file."""
    if not __changelog_file__.is_file():
        return None
    changelog = read(__changelog_file__)
    first_row = changelog.splitlines()[0].strip()
    if not first_row:
        return None
    pattern = r'^' + re.escape(__debian_pkg_name__) + r'\s+\(([^\)]+)\)'
    match = re.search(pattern, first_row)
    if not match:
        return None
    return match.group(1).strip()


__debian_version__ = get_debian_version()

if __debian_version__ is not None and __debian_version__ != '':
    __packet_version__ = __debian_version__

# -----------------------------------
def write_local_version():
    """Write the local version file."""
    local_version_file = __module_dir__ / 'local_version.py'
    local_version_file_content = textwrap.dedent('''\
        #!/usr/bin/python
        # -*- coding: utf-8 -*-
        """
        @summary: A wrapper module around the pyvmomi module to simplify work and handling.

        @author: {author}
        @contact: {contact}
        @copyright: © {cur_year} by {author}, Berlin
        """

        __author__ = '{author} <{contact}>'
        __copyright__ = '(C) {cur_year} by {author}, Berlin'
        __contact__ = {contact!r}
        __version__ = {version!r}
        __license__ = {license!r}

        # vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
        ''')

    cur_year = datetime.date.today().year
    content = local_version_file_content.format(
        author=__author__, contact=__contact__, cur_year=cur_year,
        version=__packet_version__, license=__license__)

    with local_version_file.open('wt', **__open_args__) as fh:
        fh.write(content)


# Write lib/storage_tools/local_version.py
write_local_version()

# -----------------------------------
__requirements__ = [
    'fb_tools',
    'argparse',
    'six'
]

# -----------------------------------
def read_requirements():
    """Read the requiremments.txt file."""
    req_file = __base_dir__ / 'requirements.txt'
    if not req_file.is_file():
        return

    f_content = read(req_file)
    if not f_content:
        return

    re_comment = re.compile(r'\s*#.*')
    re_module = re.compile(r'([a-z][a-z0-9_]*[a-z0-9])', re.IGNORECASE)

    for line in f_content.splitlines():
        line = line.strip()
        line = re_comment.sub('', line)
        if not line:
            continue
        match = re_module.search(line)
        if not match:
            continue
        module = match.group(1)
        if module not in __requirements__:
            __requirements__.append(module)

    print("Found required modules:\n{}\n".format(pp(__requirements__)))


read_requirements()

# -----------------------------------
__scripts__ = []

def get_scripts():
    """Collect binary script files from bin/."""
    for script in __bin_dir__.glob('*'):
        script_rel = str(script.relative_to(__base_dir__))
        if not script.is_file():
            continue
        if not os.access(str(script), os.X_OK):
            continue

        if script_rel not in __scripts__:
            __scripts__.append(script_rel)

    print("Found scripts:\n{}\n".format(pp(__scripts__)))


get_scripts()

# -----------------------------------
__data_files__ = []


# Searchin pure data files
re_usr = re.compile(r'^usr/')
re_man = re.compile(r'man/man\S+$')
if __local_usr_dir__.is_dir():
    usr_files = {}

    for f in __local_usr_dir__.glob('**/*'):
        if f.is_file():
            relpath = f.relative_to(__base_dir__)
            reldir = f.parent.relative_to(__local_usr_dir__)
            if re_man.search(str(reldir)):
                continue
            if str(reldir) not in usr_files:
                usr_files[str(reldir)] = []
            usr_files[str(reldir)].append(str(relpath))
    for udir in usr_files.keys():
        __data_files__.append((udir, usr_files[udir]))

print("Found data files:\n" + pp(__data_files__) + "\n")

# -----------------------------------

__package_data__ = {}

def create_mo_files():
    """Compile the translation files."""
    mo_files = []
    for po_path in __local_locale_dir__.glob('**/*.po'):
        po_path_rel = po_path.relative_to(__base_dir__)
        mo_path = po_path_rel.with_suffix('.mo')
        if not mo_path.exists():
            subprocess.call(['msgfmt', '-o', str(mo_path), str(po_path)])
        mo_files.append(mo_path)

    print("Found mo files:\n{}\n".format(pp(mo_files)))
    return mo_files

__pkg_mo_paths__ = create_mo_files()
__pkg_mo_files__ = []
for mo_file in __pkg_mo_paths__:
    __pkg_mo_files__.append(str(mo_file))

__package_data__[''] = __pkg_mo_files__
print("Package_data:\n" + pp(__package_data__) + "\n")

for mo_file in __pkg_mo_paths__:
    ltype = mo_file.parent.name
    lname = mo_file.parent.parent.name
    ldir = __locale_dir__ / lname / ltype
    mo_file_rel = str(mo_file).lstrip('/')
    __data_files__.append((str(ldir), [mo_file_rel]))

print("Found data files:\n" + pp(__data_files__) + "\n")

# -----------------------------------
def create_man_pages():
    """Create man pages from calling help2man from script files in bin/*."""
    man_pages = []
    man1_dir_rel = (__local_usr_dir__ / __man1_dir__).relative_to(__base_dir__)

    for script in __bin_dir__.glob('*'):
        script_rel = script.relative_to(__base_dir__)
        if not script.is_file():
            continue
        if not os.access(script, os.X_OK):
            continue

        if not man1_dir_rel.exists():
            print('Creating {!r} ...'.format(str(man1_dir_rel)))
            man1_dir_rel.mkdir(mode=0o755, parents=True)

        man_file = man1_dir_rel / (script.name + '.1.gz')
        cmd = 'help2man --no-info --no-discard-stderr'
        cmd += ' --version-string {!r}'.format(__packet_version__)
        cmd += ' --section 1'
        cmd += ' {!r}'.format(str(script_rel))
        cmd += ' | gzip -v9 > {!r}'.format(str(man_file))
        print("Executing: {}".format(cmd))

        proc = subprocess.run(cmd, shell=True, capture_output=True)
        if proc.returncode:
            msg = 'Got returncode {rc} on "help2man {f!r}".'.format(
                    rc=proc.returncode, f=script_name)
            if proc.stderr:
                msg += ' STDERR: ' + str(proc.stderr)
        else:
            man_pages.append(man_file)

    return man_pages

__man_page_paths__ = create_man_pages()
if __man_page_paths__:
    __man_pages__ = []
    for man_path in __man_page_paths__:
        __man_pages__.append(str(man_path))
    __data_files__.append((str(__man1_dir__), __man_pages__))

print("Found data files:\n" + pp(__data_files__) + "\n")

# sys.exit(0)

# -----------------------------------
class Sdist(sdist):
    """Custom ``sdist`` command to ensure that mo files are always created."""

    def run(self):
        """Compile the l18n catalog."""
        self.run_command('compile_catalog')
        # sdist is an old style class so super cannot be used.
        sdist.run(self)


# -----------------------------------
setup(
    version=__packet_version__,
    long_description=read(__readme_file__),
    scripts=__scripts__,
    requires=__requirements__,
    package_dir={'': 'lib'},
    # package_data=__package_data__,
    data_files=__data_files__,
    cmdclass={
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog,
        'sdist': Sdist,
    },
)


# =======================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
