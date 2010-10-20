from distutils.core import setup
import py2exe
import os

# Must copy the OpenGL folder from site-packages to make it work.

artfiles = []
for file in os.listdir('art'):
    if os.path.isfile('art/' + file):
        artfiles.append(('art', ['art/' + file]))

setup(console=['main.py'],
      options={
        "py2exe":{
            'includes':['ctypes', 'ctypes.util', 'logging', 'weakref'],
            'excludes':['OpenGL']
            }
        },
      data_files=artfiles
      )
