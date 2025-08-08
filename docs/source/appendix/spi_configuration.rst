SPI Configuration
=================

**Step 1**: Enable the SPI port of your Raspberry Pi (If you have enabled it, skip this; if you do not know whether you have done that or not, please continue).

.. code-block:: shell

   sudo raspi-config

**3 Interfacing options**

.. image:: ./img/image282.png

**P4 SPI**

.. image:: ./img/image285.png

**<YES>**, then click **<OK>** and **<Finish>**. Now you can use the ``sudo reboot`` command to reboot the Raspberry Pi.

.. image:: ./img/image286.png

**Step 2:** Check that the spi modules are loaded and active.

.. code-block:: shell

   ls /dev/sp*

Then the following codes will appear (the number may be different).

.. code-block:: text

   /dev/spidev0.0  /dev/spidev0.1

**Step 3:** Install Python module SPI-Py.

.. code-block:: shell

   git clone https://github.com/lthiery/SPI-Py.git
   cd SPI-Py
   sudo python3 setup.py install

.. warning::

   NOTE: This step is for python users, if you use C language, please skip.