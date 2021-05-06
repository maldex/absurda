#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sudo pip3 install simplejson flask yattag hurry.filesize

import os, sys, time, io, logging, picamera
from flask import Flask, request, Response
from yattag import Doc
from piservo import Servo

# sudo pigpiod

myservo = Servo(18)

myservo.write(180)
time.sleep(3)
myservo.write(0)
time.sleep(3)
myservo.stop()

sys.exit(0)

app = Flask(__name__, static_url_path='')
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

import RPi.GPIO as gpio


#
# servo = 18
# gpio.setmode(gpio.BCM)
# gpio.setup(servo, gpio.OUT)
#
# p = gpio.PWM(servo, 50)
# p.start(2.5)
# try:
#   while True:
#     p.ChangeDutyCycle(7.5)
#     time.sleep(1)
#     p.ChangeDutyCycle(12.5)
#     time.sleep(1)
#     p.ChangeDutyCycle(2.5)
#     time.sleep(1)
# except KeyboardInterrupt:
#   p.stop()





app = Flask(__name__, static_url_path='')
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

@app.route("/servo/<int:pin>/<int:percent>", defaults={'duration': 2})
@app.route("/servo/<int:pin>/<float:percent>/<float:duration>")
def url_set_servo(pin, percent, duration):
    # gpio.setmode(gpio.BCM)
    # gpio.setup(pin, gpio.OUT)
    # p = gpio.PWM(pin, 50)
    # p.start(0)
    # dutycycle = (percent / 100 * 5) + 2   # 2.5 ... 7.5
    # dutycycle = (percent / 100) + 1  # 2.5 ... 7.5
    # dutycycle /= 2
    # p.ChangeDutyCycle(dutycycle)
    # time.sleep(duration)
    # p.stop()
    # gpio.cleanup()
    # return F"Ok, Servo in pin {pin} to {percent}% ({dutycycle}) for {duration} second(s)"
    dutycycle = (percent / 100 + 1)  * 1000   # 1000 .... 2000
    servo = RPIO.PWM.Servo()
    servo.set_servo(pin, dutycycle)
    time.sleep(duration)
    servo.stop_servo(pin)
    return F"Ok, Servo in pin {pin} to {percent}% ({dutycycle}) for {duration} second(s)"



@app.route("/")
def index():
    doc, tag, text = Doc().tagtext()

    with tag('hr'):
        pass
    with tag('h2'):
        text("request.args")
    with tag('pre'):
        for k,v in request.args.items():
            doc.asis(str(k) + ': ' + str(v) + os.linesep)


    with tag('hr'):
        pass
    with tag('h2'):
        text("request.environ")
    with tag('pre'):
        for k, v in request.environ.items():
            doc.asis(str(k) + ': ' + str(v) + os.linesep)
    return Response(doc.getvalue(), mimetype='text/html;charset=UTF-8')


if __name__ == '__main__':
    logging.info("starting flask")
    app.run(host='0.0.0.0', port=3002, debug=False)

