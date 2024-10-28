import os
import shutil

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext

package_name = 'pupilio'
build_file = 'build_number.txt'


def get_build_number():
    if os.path.exists(build_file):
        with open(build_file, 'r') as f:
            build_number = int(f.read().strip())
    else:
        build_number = 0
    build_number += 1
    # 将新的 build 号写入文件
    with open(build_file, 'w') as f:
        f.write(str(build_number))
    return build_number


build_number = get_build_number()


class CustomBuildExt(build_ext):
    def run(self):
        # Ensure the build_ext is run first
        build_ext.run(self)
        # Copy the DLL file to the build/lib/my_package/lib directory
        build_lib = os.path.join(self.build_lib, package_name, 'lib')
        os.makedirs(build_lib, exist_ok=True)
        shutil.copy('pupilio/lib/DeepGazeET_Bk.dll', build_lib)
        shutil.copy('pupilio/lib/libfilter.dll', build_lib)


major_version = '1'
minor_version = '1'
patch_version = '2'

setup(
    name="pupilio",
    version=f"{major_version}.{minor_version}.{patch_version}",
    author="Pupilio",
    author_email="zhugc2016@gmail.com",
    description="Pupilio Library",
    url="https://deep-gaze.com/sdk/python",
    packages=find_packages(),

    package_data={
        'pupilio': ['lib/*.dll', 'resources/*', "local_config/*", "asset/*"],
    },

    install_requires=[
        'numpy', 'pygame', 'websockets', 'opencv-python',
    ],

    cmdclass={'build_ext': CustomBuildExt},
)
