# Python/RaspBerry part that should run on the raspberry

## RaspBerry Setup instructions
- use the 'Raspberry Pi OS with desktop and recommended software' image of Raspberry Pi OS
- I trust you can burn these 8GB yourself to your SD Card.
- I also trust you'll know how to get a console/bash/ssh/shell.
- Just simply copy paste the following commands into your shell.

#### 
running `cat /etc/cpuinfo` and `sudo raspi-config`, do the following:
- 5 Internationalization -> L3 Keyboard -> German Switzerland & enable alt-ctrl-backspace to kill X11
- 5 Internationalization -> L2 Timezone -> Europe/Zurich
- 4 Performance Options -> P2 GPU Memory -> 128
- 3 Interface Options -> P5 I2C -> yes
- 3 Interface Options -> P2 SSH -> yes
- 3 Interface Options -> P1 Camera -> yes
- 2 Display Options -> D4 Screen Blanking -> no
- 1 System Options -> S4 Hostname -> rpi-serialnr (eg. rpi-a8df)
- 1 System Options -> S7 Splash Screen -> no
- 1 System Options -> S3 Password -> set a new one

#### install other stuff
```bash
sudo apt-get update
sudo apt-get install -yq mc git iptraf-ng fswebcam linux-cpupower ntp ntpdate python3-pip html2ps wkhtmltopdf
```

### more adjustments
```bash
sudo sed -i '/pool/ s/^#*/#/' /etc/ntp.conf
sudo sed -i '/^#pool 0.*/ipool time.gebaschtel.ch iburst' /etc/ntp.conf
sudo systemctl enable --now ntp

sudo sed -i '/^exit 0/i# systemctl stop ntp; ntpdate time.gebaschtel.ch; systemctl start ntp\
cpupower frequency-set -g ondemand > /dev/null\
echo "\`date`\" | mutt -s "system rebooted" log@gebaschtel.ch\
' /etc/rc.local

sudo bash -c 'cat << EOF >> /etc/rsyslog.conf 
*.*  @@syslog.bnet.gebaschtel.ch:514
EOF'
sudo systemctl restart syslog
```

#### install python libraries
```bash
sudo pip3 install simplejson flask yattag hurry.filesize wiringpi piServoCtl arrow pathlib python-libmagic 
```

### clone project and enable services
```bash
cd ~
git clone https://github.com/maldex/absurda.git
sudo systemctl enable --now /home/pi/absurda/RasPy/CamService.service
sudo systemctl enable --now /home/pi/absurda/RasPy/OpenCvService.service
sudo systemctl enable --now /home/pi/absurda/RasPy/TtsService.service
sudo systemctl enable --now /home/pi/absurda/RasPy/AbsurdaService.service
```


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
