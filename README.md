# Aerogenerator
This is intended to be a simulation of a wind generator blades' position and generator orientation.
### Overview
The project was made with an Arduino MEGA interfacing it with a PC. At some point of the development, a Raspberry Pi B was used. On the PC side (or Raspberry) the python 2.7 script must be running.
The Arduino is connected to:
 - One stepper motor: which would rotate the generator to point out to in the wind direction in order to maximize power generation
 - One servo motor: this is used to change a blade angle attack. In fact, this should be 3 servo motors, one for each blade.
 - One potentiometer: So you could move by hand the blades' angle attack.
 - One button: when you push the button, the value of the potentiometer is translated into the blades' angle attack.
 
The script has PyMata as dependecy. You can find the repo right [here](https://github.com/MrYsLab/PyMata "PyMata repo"), or you can download it directly thru pip

### Beware!!
The Arduino is loaded with a modified version of the FirmataPlus program. The modification lies within the stepper library. This was made, because the stepper motor used is a 28BYJ-48 and the driver is a ULN2003.
The driver is a darlington transistor array, so you need to send, from the Arduino, the right signal order so you can drive as you need the stepper motor. The Arduino is configured to use the full-step drive

