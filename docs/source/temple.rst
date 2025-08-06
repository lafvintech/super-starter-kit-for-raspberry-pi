==================
1.1.1 Blinking LED
==================

Introduction
------------
xxxxxx

Components
----------

.. image:: ./img/list/blinking_led_list.png


Connect
-------



Code
----
For C Languag
~~~~~~~~~~~~~~~~~~
**1. Navigate to the Code's Folder**

First, you need to tell your Raspberry Pi where to find the C code file. You do this by using the `cd` (change directory) command.

.. code-block:: shell

   cd ~/super-starter-kit-for-raspberry-pi/c/1.1.1/

.. image:: ./img/cd-dir.png

.. note::

   The `~` symbol is a shortcut for your home directory. This command tells the Pi to navigate from your home folder into the specific folder for this project.

**2. Compile the Code**

The C code you've written is like a recipe in a human language. To make the Raspberry Pi understand it, you need to "compile" it into an executable program. We use a program called `gcc` for this, which acts like a translator.

.. code-block:: shell

   gcc 1.1.1_BlinkingLed.c -o BlinkingLed -lwiringPi

.. note::

   Let's break down this command:
   * `gcc`: The name of our compiler program.
   * `1.1.1_BlinkingLed.c`: The source code file you want to compile.
   * `-o BlinkingLed`: This tells the compiler to create an executable file named `BlinkingLed`. The `-o` stands for "output".
   * `-lwiringPi`: This links the `wiringPi` library. A library is a collection of pre-written code that makes it easier to perform common tasks, like controlling GPIO pins.

**3. Run the Program**

Now that you have your compiled program, you can run it.

.. code-block:: shell

   sudo ./BlinkingLed

.. note::

   * `sudo`: This command stands for "Superuser Do" and gives you administrator privileges, which are necessary for controlling hardware like GPIO pins.
   * `./BlinkingLed`: This tells the Pi to run the `BlinkingLed` program located in the current directory (`./`).

.. image:: ./img/code-run1.png

After running the command, you should see your LED start to blink!

**4. Edit the Code (Optional)**

If you want to make changes to the code, you first need to stop the current program by pressing `Ctrl + C`. Then, you can use the `nano` text editor to open the file.

.. code-block::

   nano 1.1.1_BlinkingLed.c

.. note::
   `nano` is a simple, command-line based text editor. After making your changes in nano, press `Ctrl+X`, then `Y` to confirm you want to save, and finally `Enter` to exit. You'll need to re-run the compile and run steps to see your changes take effect.

For Python Languag
~~~~~~~~~~~~~~~~~~
**Go to the folder of the code.**

.. code-block:: shell

   cd ~/super-starter-kit-for-raspberry-pi/python/1.1.1/

**Run**

.. code-block:: shell

   python 1.1.1_BlinkingLed.py

After running the command, you should see your LED start to blink!

Phenomenon
----------

.. image:: ./img/phenomenon/111.jpg
