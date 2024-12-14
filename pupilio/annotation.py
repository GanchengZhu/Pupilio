#!/usr/bin/bash
# _*_ coding: utf-8 _*_
# Author: GC Zhu
# Email: zhugc2016@gmail.com

import warnings
from functools import wraps


# Decorator to mark functions as deprecated with version information
def deprecated(version):
    """
    A decorator to mark functions as deprecated with a specified version.

    This decorator issues a warning whenever a deprecated function is called,
    informing the user about the deprecation and the version it was introduced in.

    Args:
        version (str): The version in which the function was deprecated.

    Returns:
        function: The decorated function that issues a warning when called.
    """

    def decorator(func):
        """
        The actual decorator that wraps the target function.

        Args:
            func (function): The function being decorated.

        Returns:
            function: A wrapper function that adds deprecation warning functionality.
        """

        @wraps(func)  # Ensures the decorated function retains its original name and docstring
        def wrapper(*args, **kwargs):
            """
            The wrapper function that issues the deprecation warning and calls the original function.

            Args:
                *args: Positional arguments passed to the original function.
                **kwargs: Keyword arguments passed to the original function.

            Returns:
                The return value of the original function.
            """
            warnings.warn(
                f"The function '{func.__name__}' is deprecated since version {version} and will be removed in"
                f" future versions. Please use the new alternative.",
                DeprecationWarning,  # Specifies that this is a deprecation warning
            )
            return func(*args, **kwargs)  # Calls the original function

        return wrapper  # Return the wrapped version of the function

    return decorator  # Return the decorator function
