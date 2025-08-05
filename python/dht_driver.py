#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename    : dht_driver.py
Description : A Python library/wrapper for our custom C-based DHT11 driver.
              This module provides a clean, object-oriented interface.
modification: 2025/08/01
"""

import ctypes
import os

class DHT:
    """
    A Python class to interact with the DHT11 sensor via a custom C library.
    This class handles loading the library, defining the C function signatures,
    and providing a simple read() method.
    """

    # --- Private Class-level variables for C library interaction ---
    _dht_lib = None
    _dht11_read_func = None

    # --- C Data Structures and Constants ---
    class _DHT_Data(ctypes.Structure):
        """Maps to the DHT_Data struct in the C header."""
        _fields_ = [("temperature_celsius", ctypes.c_float),
                    ("humidity_percent", ctypes.c_float)]

    _DHT_SUCCESS = 0
    
    def __init__(self, c_library_path="./dht_c_driver.so"):
        """
        Initializes the DHT driver by loading the C shared library.
        
        Args:
            c_library_path (str): The path to the compiled .so file.
                                  Defaults to the current directory.
        """
        if DHT._dht_lib is None: # Load the library only once
            self._load_library(c_library_path)
            self._setup_functions()
            self._initialize_wiringpi()

    def _load_library(self, path):
        """Loads the C shared library."""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(
                f"C library not found at '{abs_path}'.\n"
                "Please compile it first by running:\n"
                "gcc -shared -fPIC -o dht_c_driver.so dht_c_driver.c -lwiringPi"
            )
        try:
            DHT._dht_lib = ctypes.CDLL(abs_path)
        except OSError as e:
            raise OSError(f"Error loading C library: {e}")

    def _setup_functions(self):
        """Sets up the ctypes function signatures."""
        try:
            DHT._dht11_read_func = DHT._dht_lib.dht11_read
            DHT._dht11_read_func.argtypes = [ctypes.c_int, ctypes.POINTER(DHT._DHT_Data)]
            DHT._dht11_read_func.restype = ctypes.c_int
        except AttributeError:
            raise AttributeError(
                "Function 'dht11_read' not found in the C library. "
                "Please check the C code and recompile."
            )

    def _initialize_wiringpi(self):
        """Initializes the wiringPi library, which is a prerequisite for our C code."""
        if DHT._dht_lib.wiringPiSetup() == -1:
            raise RuntimeError("Failed to initialize wiringPi via C library.")

    def read(self, pin):
        """
        Reads temperature and humidity from the DHT11 sensor.

        This method calls the underlying C function, handling the creation
        of the data structure and interpreting the result.

        Args:
            pin (int): The wiringPi pin number the sensor is connected to.

        Returns:
            tuple: A tuple containing (humidity, temperature) on success.
                   Returns (None, None) on failure.
        """
        sensor_data = DHT._DHT_Data()
        status = DHT._dht11_read_func(pin, ctypes.byref(sensor_data))

        if status == DHT._DHT_SUCCESS:
            return (sensor_data.humidity_percent, sensor_data.temperature_celsius)
        else:
            return (None, None)
