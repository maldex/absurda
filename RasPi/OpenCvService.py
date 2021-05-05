#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from flask import Flask, request, Response, jsonify, abort, render_template, redirect, send_from_directory
from yattag import Doc
import os, sys, requests, time, datetime, threading, logging, psutil, socket, smbus, subprocess, requests, cv2, numpy, base64, io
import simplejson as json

faceCascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml')

app = Flask(__name__, static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024    # 16 MB
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# https://www.geeksforgeeks.org/get-post-requests-using-python/

@app.route('/test', methods=["GET"])
def url_test():
    plain_picture = requests.get("http://127.0.0.1:3000/pic.jpeg", {'width': 640, 'height': 400}).content
    faced_picture = requests.post("http://127.0.0.1:3333/detect_faces", data={'image': base64.b64encode(plain_picture)} ).content
    return Response(faced_picture, mimetype='image/jpeg')

@app.route('/detect_faces', methods=['GET', 'POST'])
def url_detect_faces():
    pic = base64.b64decode(request.values['image'])
    arr = numpy.frombuffer(pic, dtype='uint8')
    frame = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        color = (0, 255, 0)
        cv2.line(frame, (x, y), (x+int(w/2), y), color, 5)
        cv2.line(frame, (x, y), (x, y+int(h/2)), color, 5)
        cv2.line(frame, (x+w, y+h), (x+int(w/2), y+h), color, 5)
        cv2.line(frame, (x+w, y+h), (x+w, y+int(h/2)), color, 5)




        # frame = cv2.putText(frame, "face", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4, cv2.LINE_8)

    rc, jpeg_pic = cv2.imencode(".jpg", frame)
    return Response(jpeg_pic.tobytes(), mimetype='image/jpeg')



@app.route('/', methods=["GET"])
def url_index():
    doc, tag, text = Doc().tagtext()

    with tag('h3'):   text('flask registered endpoints')
    with tag('pre'):
        endpoints = list(map(lambda x: repr(x), app.url_map.iter_rules()))
        endpoints.sort()
        for endpoint in endpoints: text(endpoint + '\n')
    with tag('hr'): text('request.args')
    with tag('pre'):
        for k, v in request.args.items(): text(str(k) + ': ' + str(v) + '\n')
    with tag('hr'): text('request.environ')
    with tag('pre'):
        for k, v in request.environ.items(): text(str(k) + ': ' + str(v) + '\n')
    return Response(doc.getvalue(), mimetype='text/html;charset=UTF-8')

if __name__ == "__main__":
    #DA_thread.start()
    app.run(debug=False, host='0.0.0.0', port=3001)


