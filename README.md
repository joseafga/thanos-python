# Thanos

Robot for UNIP Assis project!

It read XBox 360 or One gamepad inputs, translate to PWM signal value and transmits via bluetooth communication.
For this project we used a [Arduino board with HC-06 module](https://github.com/joseafga/thanos-arduino) to receive signal and control motor using H-bridge.

## Require
- Python 3
- `pip install inputs`
- `pip install pyserial`
- `pip install pybluez`
- XBox 360/One gamepad
- bluetooth adapter

## Install and Use
Create a Python virtualenv install dependencies (see require) and active it.
Make sure you bluetooth adapter is enable then run `main.py`:

    $ python main.py

Now you can connect to HC-06 module and send commands using a gamepad.

## License
**MIT License**  
See [LICENSE](LICENSE) file for details.
