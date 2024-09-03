import os
import shutil

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext

package_name = 'deepgaze'


class CustomBuildExt(build_ext):
    def run(self):
        # Ensure the build_ext is run first
        build_ext.run(self)
        # Copy the DLL file to the build/lib/my_package/lib directory
        build_lib = os.path.join(self.build_lib, package_name, 'lib')
        os.makedirs(build_lib, exist_ok=True)
        shutil.copy('deepgaze/lib/DeepGazeET.dll', build_lib)
        shutil.copy('deepgaze/lib/libfilter.dll', build_lib)


setup(
    name="deepgaze",
    version="1.1.0",
    author="DeepGaze",
    author_email="zhugc2016@gmail.com",
    description="DeepGaze Library",
    url="https://deep-gaze.com/sdk/python",
    packages=find_packages(),

    package_data={
        'deepgaze': ['lib/*.dll', 'resources/*', "local_config/*", "asset/*"],
    },

    install_requires=[
        'numpy', 'pygame', 'websockets'
    ],

    cmdclass={'build_ext': CustomBuildExt},
)
