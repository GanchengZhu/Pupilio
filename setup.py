import os
import shutil

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext

package_name = 'pupilio'


class CustomBuildExt(build_ext):
    def run(self):
        # Ensure the build_ext is run first
        build_ext.run(self)
        # Copy the DLL file to the build/lib/my_package/lib directory
        build_lib = os.path.join(self.build_lib, package_name, 'lib')
        os.makedirs(build_lib, exist_ok=True)
        shutil.copy('pupilio/lib/DeepGazeET.dll', build_lib)
        shutil.copy('pupilio/lib/libfilter.dll', build_lib)


setup(
    name="pupilio",
    version="1.1.0",
    author="Pupilio",
    author_email="zhugc2016@gmail.com",
    description="Pupilio Library",
    url="https://deep-gaze.com/sdk/python",
    packages=find_packages(),

    package_data={
        'pupilio': ['lib/*.dll', 'resources/*', "local_config/*", "asset/*"],
    },

    install_requires=[
        'numpy', 'pygame', 'websockets'
    ],

    cmdclass={'build_ext': CustomBuildExt},
)
