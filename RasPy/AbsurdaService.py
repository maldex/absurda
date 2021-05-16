#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sudo pip3 install simplejson flask yattag hurry.filesize
# sudo systemctl stop AbsurdaService

import os, sys, time, io, logging, picamera, requests, base64, datetime, subprocess
from flask import Flask, request, Response, render_template
from yattag import Doc
from hurry.filesize import size
from pprint import pprint

app = Flask(__name__, static_url_path='', template_folder=os.getcwd() + '/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024    # 16 MB
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

@app.route('/test', methods=["GET"])
def url_test():
    plain_picture = requests.get("http://127.0.0.1:3000/pic.jpeg", {'width': 640, 'height': 400}).content
    faced_picture = requests.post("http://127.0.0.1:3001/detect_faces", data={'image': base64.b64encode(plain_picture)} ).content
    return Response(faced_picture, mimetype='image/jpeg')

@app.route('/report', methods=["GET"])
def url_get_pic():
    picture = requests.get("http://127.0.0.1:3000/pic.jpeg", {'width': 640, 'height': 400}).content
    picture = requests.post("http://127.0.0.1:3001/detect_faces", data={'image': base64.b64encode(picture)} ).content

    pre = {'data1': "some text",
           'data2': "19912345-335",
           'hallo': "sunny shiny",
           'datetime':  datetime.datetime.now().strftime('%y.%m.%d %H:%M:%S')}

    post = """***************************
* THANK YOU FOR YOUR DATA *
***************************"""

    report = render_template("report.html",
                            current_state="tuiiii",
                            pre=pre,
                            pic=base64.b64encode(picture).decode(),
                            post=post)


    report_file = "/tmp/report-" + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + ".html"
    with open(report_file, 'w') as f:
        f.write(report)

    if 'print' in request.values and str(request.values['print']).lower() == 'true':
        subprocess.Popen(["bash", "AbsurdaPrint.sh", report_file])

    return report

@app.route("/")
def index():
    doc, tag, text = Doc().tagtext()

    with tag('h2'):
        text("Get Data")
    with tag('a', ('href', '/report')): text('report')
    text(' - ')
    with tag('a', ('href', '/report?print=true')):
        text('report(print)')
    text(' - ')
    with tag('a', ('href', '/test')): text('test')

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
    app.run(host='0.0.0.0', port=3333, debug=False)

