#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from flask import Flask, request, Response, jsonify, abort, render_template, redirect, send_from_directory
from yattag import Doc
import os, sys, requests, time, datetime, threading, logging, psutil, socket, smbus, subprocess, requests
import simplejson as json


app = Flask(__name__, static_url_path='')
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app_start_time = time.time()

# https://www.geeksforgeeks.org/get-post-requests-using-python/

@app.route('/test', methods=["GET"])
def url_test():
    r = requests.get("http://127.0.0.1:3000/pic.jpeg", {'w': 1280, 'h': 720})
    plain_picture = r.content
    return Response(plain_picture, mimetype='image/jpeg')




@app.route('/', methods=["GET"])
def url_index():
    doc, tag, text = Doc().tagtext()

    with tag('h3'):
        with tag('a', href='/raw.json'): text("raw.json")

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
    app.run(debug=False, host='0.0.0.0', port=3333)



