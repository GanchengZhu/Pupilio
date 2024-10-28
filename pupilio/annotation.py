#!/usr/bin/bash
# _*_ coding: utf-8 _*_
# Author: GC Zhu
# Email: zhugc2016@gmail.com

import warnings
from functools import wraps


# Decorator to mark functions as deprecated with version information
def deprecated(version):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"The function '{func.__name__}' is deprecated since version {version} and will be removed in future versions. Please use the new alternative.",
                DeprecationWarning,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
