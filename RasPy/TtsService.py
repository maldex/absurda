#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sudo pip3 install simplejson flask yattag hurry.filesize

import os, sys, time, io, logging, threading, arrow, pathlib, subprocess
from flask import Flask, request, Response, render_template, send_file
from yattag import Doc
from datetime import datetime
from hurry.filesize import size
from pprint import pprint

templates_dir = os.getcwd() + '/templates'
os.chdir('/tmp')
logging.basicConfig(level=logging.DEBUG)


def text2speech(text="burp", lang='it-IT', id=None):
    if id is None:
        id = "tts-" + lang + "-" + datetime.now().strftime('%Y%m%d%H%M%S%f')
    outtxt = id + ".txt"
    outwav = id + ".wav"
    with open(outtxt, 'w') as f:
        f.write(text)
    subprocess.call(["pico2wave", "-l", lang, "-w", outwav, text])
    return outwav



class CleanUpThread(threading.Thread):
    def __init__(self, workdir='./', age=300, globs=['*.wav','*.mp3','*.txt'], interval=30, debug=False):
        threading.Thread.__init__(self)
        self.workdir, self.age, self.globs, self.interval, self.debug = workdir, age, globs, interval, debug
        self.alive = False
        if self.debug: logging.debug("CleanUpThread: instanciated")

    def stop(self):
        self.alive = False

    def run(self):
        if self.debug: logging.debug("CleanUpThread: thread started")
        self.alive = True
        while self.alive:
            self.run_errands()
            time.sleep(self.interval)
        if self.debug: logging.debug("CleanUpThread: stopped")


    def run_errands(self):
        if self.debug: logging.debug("CleanUpThread: run the errands")
        criticalTime = arrow.now().shift(seconds=-self.age)
        for pattern in self.globs:
            for item in pathlib.Path(self.workdir).glob(pattern):
                if item.is_file():
                    itemTime = arrow.get(item.stat().st_mtime)
                    if self.debug: logging.debug(F"{criticalTime} - {itemTime} - {item.absolute()}")
                    if itemTime < criticalTime:
                        logging.debug(F"removing {item.absolute()} after {criticalTime - itemTime}")
                        os.remove(item.absolute())


app = Flask(__name__, static_url_path='', template_folder=templates_dir)
app.logger.setLevel(logging.DEBUG)


@app.route("/")
def index():
    doc, tag, text = Doc().tagtext()

    with tag('a', ('href', '/tts')): text('TTS')


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


@app.route("/tts", methods=['GET', 'POST'])
def url_tts():
    debug = None
    if 'op' in request.values:
        return handle_op(mode=request.values['op'], text=request.values['text'], lang=request.values['lang'])

    languages = ["en-US", "en-GB", "de-DE", "fr-FR", "it-IT", "es-ES"]
    if 'lang' in request.values:
        languages.remove(request.values['lang'])
        languages.insert(0, request.values['lang'])

    if 'text' in request.values:
        text = request.values['text']
    else:
        text = """By Jove, my quick study of lexicography won a prize!"""

    return render_template("tts.html",
                           page_title="Text2Speech",
                           languages=languages,
                           text=text,
                           debug=debug)

@app.route("/files/<path:file>")
def url_send_file(file):
    file_path = os.path.join(os.getcwd(), file)
    mime_type = "text/plain"
    if file.endswith(".wav"):
        mime_type = "audio/wav"
    return send_file(file_path, mimetype=mime_type, as_attachment=True)


def handle_op(mode, text="test", lang="en-US"):
    outwav = text2speech(text=text, lang=lang)

    if mode == "download":
        return url_send_file(outwav)

    doc, tag, text = Doc().tagtext()
    with tag("title"):
        text("playback " + mode )

    with tag('form'):
        with tag('input', type="button", value="back", onclick="history.back()"):
            pass

    if mode == "aplay":
        subprocess.Popen(["aplay", outwav ])
        return Response(doc.getvalue(), mimetype='text/html;charset=UTF-8')

    if mode == "browser":
        with tag('audio', id='player1', controls='controls', autoplay=True):
            with tag('source', src='/files/' + outwav, type='audio/x-wav'):
                pass
        return Response(doc.getvalue(), mimetype='text/html;charset=UTF-8')

    return "unknown method " + mode



if __name__ == '__main__':
    MyCleanUpThread = CleanUpThread(globs=['tts-*.wav','tts-*.txt'])
    MyCleanUpThread.start()
    logging.info("starting flask")
    app.run(host='0.0.0.0', port=3002, debug=False)
    MyCleanUpThread.stop()
