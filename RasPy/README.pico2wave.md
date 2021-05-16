# text to speech synthesis

#### https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)#Pico_Text_to_Speech
#### https://cstan.io/?p=11840&lang=en
```bash
cd /usr/local/src
sudo sed -i 's/^#deb-src/deb-src/g' /etc/apt/sources.list
sudo apt-get update
sudo apt-get install -y autoconf libtool help2man libpopt-dev debhelper

sudo rm -rf svox*
sudo apt-get source libttspico-utils

cd svox-1.0*/

time sudo dpkg-buildpackage -rfakeroot -us -uc

cd ..

sudo dpkg -i libttspico-data_*all.deb libttspico-utils*.deb libttspico0*.deb

cd ~

pico2wave  -w ~/test.wav -l de-DE "Franz jagt im komplett verwahrlosten Taxi quer durch Zürich" && aplay ~/test.wav
```