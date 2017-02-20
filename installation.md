# INSTALLATION

The software can be used on Windows, Linux and MacOS. It is written entirely in Python3.

## Windows

You need to install python 3 in order to use the software. You can download it here : [https://www.python.org/downloads/](https://www.python.org/downloads/)

Some additional python packages also need to be installed. Open a terminal \(Press Win+E then type 'cmd' and press Enter\), and enter the following command :

```
pip install Pillow mss
```

To run the program, change your current directory to its root folder

```
cd /path/to/game-stats-manager/
```

And then run the main.py file with python

```
python src/main.py
```

Alternately, you can run the main\_fr.py file to launch the French version.

## GNU/Linux

Python 3 must be installed on your distribution. Additional dependencies are required. They can be installed with pip.

```bash
pip install Pillow mss
```

Additional packages may be needing depending on your distribution.

If when trying to run the program you get the error :

> TclError: can't find package Tix

Then install the tix package of your distribution.

**Debian-based :**

```
apt-get install tix-dev
```

**Arch :**

```
pacman -S tix
```

If when trying to run the program you get the error :

> import \_tkinter \# If this fails your Python may not be configured for Tk
>
> ImportError: No module named \_tkinter

Install the tk-devel package of your distribution.

**Debian-based :**

```
apt-get install tk-dev
```

**Arch :**

```
pacman -S tk
```

**Fedora :**

```
dnf install tk-devel tkinter
```

For launching the program, open a terminal, move to the root folder of the program, and run the command :

```
python src/main.py
```

Alternately, you can launch the main\_fr.py file to run the French version.

