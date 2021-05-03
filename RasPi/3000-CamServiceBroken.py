#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sudo pip3 install simplejson flask yattag hurry.filesize

import os, sys, time, io, logging, picamera
from flask import Flask, request, Response
from yattag import Doc
from hurry.filesize import size



class MyPyPiCam(object):
    def __init__(self, device=0, width=1920, height=1080, rotation=0, contrast=0, brightness=50, saturation=0, sharpness=0, effect='none', awb='auto', exposure='auto'):
        self.camera = picamera.PiCamera(0)
        self.camera.resolution = (width, height)
        self.camera.rotation = rotation
        self.camera.brightness = brightness
        self.camera.saturation = saturation
        self.camera.image_effect = effect
        self.camera.sharpness = sharpness
        self.camera.contrast = contrast
        self.camera.awb_mode = awb
        self.camera.exposure_mode = exposure
        self.camera.led = False
        self._preview = False
        self.last_pic = io.BytesIO()
        self.set_display_preview(False)

    def get_display_preview(self):
        return self._preview

    def set_display_preview(self, value=True):
        if value == self.get_display_preview():
            return None
        self._preview = value
        if value:
            return self.camera.start_preview()
        else:
            return self.camera.stop_preview()

    def capture(self, text=None):
        text = ""   # datetime.today().strftime('%Y.%m.%d %H:%M:%S.%f')
        start = time.time()
        self.camera.annotate_text = text
        self.camera.annotate_text_size = 72
        try:
            new_pic = io.BytesIO()
            # if width is None or height is None:
            self.camera.capture(new_pic, format='jpeg')
            # else:
            #     self.camera.capture(new_pic, format='jpeg', resize=(width, height))
            logging.info("captured %s in %.3f sec" % (size(sys.getsizeof(new_pic)), (time.time() - start)))
            self.last_pic = new_pic
        except picamera.exc.PiCameraValueError as e:
            logging.warning(str(e) + " - using last picture")

        return io.BytesIO(self.last_pic.getvalue())







app = Flask(__name__, static_url_path='')
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def index():
    doc, tag, text = Doc().tagtext()

    with tag('h2'):
        text("Get Data Area")

    with tag('big'):
        with tag('a', ('href', '/pic.jpeg?w=640&h=400')): text('VGA')
        text(' - ')
        with tag('a', ('href', '/pic.jpeg?w=1280&h=720')): text('SD')
        text(' - ')
        with tag('a', ('href', '/pic.jpeg?w=1920&h=1080')): text('HD')
        text(' - ')
        with tag('a', ('href', '/pic.jpeg?w=3440&h=1440')): text('1440p')
        text(' - ')
        with tag('a', ('href', '/pic.jpeg?w=3840&h=2160')): text('UHD')
        text(' - ')
        with tag('a', ('href', '/pic.jpeg')): text('pic')
        with tag('br'): pass
        with tag('a', ('href', '/pic.jpeg?w=640&h=400&e=emboss')): text('emboss')


    with tag('hr'):
        pass
    # with tag('h2'):
    #     text("Admin Area")
    #
    # if not 'mode' in request.args:
    #     with tag('table'):
    #         with tag('tr'):
    #             with tag('form', ('method', 'get')):
    #                 with tag('td'):
    #                     if MyCam.get_display_preview(): v = "stop preview"
    #                     else: v = "start preview"
    #                     with tag('input', ('type', 'submit'), ('name', 'mode'), ('value', v)):
    #                         pass
    #
    # else: # mode was specified
    #     if request.args['mode'].isupper():
    #         with tag('h1'):
    #             text("ARE U SURE?")
    #         with tag('form', ('method', 'get')):
    #             with tag('input', ('type', 'submit'), ('name', 'mode'), ('value', request.args['mode'].lower())):
    #                 pass
    #
    #     if request.args['mode'].endswith("preview"):
    #         MyCam.set_display_preview(request.args['mode'].startswith("start"))
    #         with tag('meta', ('http-equiv', 'refresh'), ('content', '0; url=' + request.environ['PATH_INFO'])):
    #             pass
    #         return doc.getvalue()
    #
    #     if request.args['mode'] == "start preview":
    #         MyCam.set_display_preview(True)
    #


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

@app.route("/pic.jpeg")
def get(width=None, height=None, effects='none', exposure='auto'):
    if 'w' in request.args:
        width = int(request.args['w'])
    if 'h' in request.args:
        height = int(request.args['h'])
    # obj = MyCam.capture(width=width, height=height)
    camera = MyPyPiCam(width=width, height=height)
    picture = camera.capture()
    return Response(picture.getvalue(), mimetype='image/jpeg')

# https://picamera.readthedocs.io/en/release-1.10/api_camera.html
# effects:  none, negative, solarize, sketch, denoise, emboss, oilpaint, hatch, gpen, pastel, watercolor, film, blur, saturation, colorswap, washedout, posterise, colorpoint, colorbalance, cartoon, deinterlace1 und deinterlace2
# awb: off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, und horizo
# exposure: off, auto, night, nightpreview, backlight, spotlight, sports, snow, beach, verylong, fixedfps, antishake, und firework


if __name__ == '__main__':
    logging.info("starting flask")
    app.run(host='0.0.0.0', port=3000, debug=False)

