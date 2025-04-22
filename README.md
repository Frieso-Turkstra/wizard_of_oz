# Wizard of Oz

This application implements remote control of a Temi robot, thus allowing researchers to conduct a [Wizard of Oz experiment](https://en.wikipedia.org/wiki/Wizard_of_Oz_experiment).

## Functionality 

A graphical interface is provided to send commands to the robot. These commands include both motor and speech controls:
* Send the robot to a predefined location on a map
* Navigate freely using the camera and the arrow/wasd keys
* Tilt the camera up and down
* Let the robot say something, use either freely typed text or predefined templates for faster response times
* Display on the GUI what the user has said to the robot

## How to use

Install the sample app on your Temi. Check out the official Temi documentation for instructions if you are unsure how to do this.
On the computer that you want to control Temi with, you should have the `wizard-of-oz` directory and the necessary requirements:

`pip install wizard-of-oz/requirements.txt`

Make sure the computer and Temi are on the same WiFi network. Open the app on Temi and if necessary, accept any permission requests.
Now run the graphical user interface on the computer with this command: 

`python wizard_of_oz/main.py`
