# HOWTO : in a command line prompt :
# - change your path to the directory where the setup and main file are located
# - lauch it with : "python setup.py py2exe"

from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 2, 'compressed': True}},
    windows = [{'script': "main.py",
                'icon_resources': [(1, 'icon.ico')]
               }
    ],
    zipfile = None,
)
