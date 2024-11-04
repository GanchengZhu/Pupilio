#!/usr/bin/bash
# _*_ coding: utf-8 _*_
# Author: GC Zhu
# Email: zhugc2016@gmail.com
import ctypes
import os
import sys

# current_dir = os.path.abspath(os.path.dirname(__file__))

lib_dir = os.path.abspath(os.path.dirname(__file__))
os.add_dll_directory(lib_dir)
os.environ['PATH'] = os.environ['PATH'] + ';' + lib_dir
sys.path.append(lib_dir)

dll_path = os.path.join(lib_dir, 'PupilioET.dll')
et_native_lib = ctypes.CDLL(dll_path, winmode=0x8)


dll_path = os.path.join(lib_dir, 'libfilter.dll')
filter_native_lib = ctypes.CDLL(dll_path, winmode=0x8)