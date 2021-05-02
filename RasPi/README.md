# Python/RaspBerry part that should run on the raspberry

## RaspBerry Setup instructions
- use the 'Raspberry Pi OS with desktop and recommended software' image of Raspberry Pi OS
- I trust you can burn these 8GB yourself to your Raspi.
- I also trust you'll know how to get a console/bash/ssh/shell.
- Just simply copy paste the following commands into your shell.

#### just fresh Raspberry basic tasks
```bash
# remove some space-consuming packets
sudo apt-get purge -y wolfram-engine libreoffice*
# simple cleanup and update
sudo apt-get clean -y
sudo apt-get autoremove -y
sudo apt-get update
sudo apt-get upgrade -y
# yes, also linux should be rebooted after an update
sudo reboot
```
