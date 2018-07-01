import collections
import cv2
import http
import importlib
import os
import re
import sys
import threading
import time
import urllib
from socketserver import ThreadingMixIn
from SimpleHTTPSAuthServer3 import HTTPSAuthServer, AuthHandler

class CamHandler(AuthHandler):
    def __init__(self, request, client_address, server):
        self.html_404_page = '<h1>NOT FOUND</h1>'
        super().__init__(request, client_address, server)

    def get_html(self, img_src='cam.mjpg'):
        return '<img src="{}"/>'.format(img_src)

    def do_GET(self):
        if not super().do_GET():
            return

        parsed_url = urllib.parse.urlparse(self.path)
        dirpath, filename = os.path.split(parsed_url.path)
        query = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
        root, ext = os.path.splitext(filename)
        if filename.endswith('.mjpg'):
            self.send_response(http.client.OK)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            filters = collections.OrderedDict()
            for key in query:
                try:
                    sys.dont_write_bytecode = True
                    filter_module = importlib.import_module('filter.' + key)
                    filter = filter_module.Filter(query[key])
                    filters[filter] = query[key]
                    sys.modules.pop('filter.' + key)
                except ModuleNotFoundError as e:
                    print(e)
                except AttributeError as e:
                    sys.modules.pop('filter.' + key)
                    print(e)
                finally:
                    sys.dont_write_bytecode = False

            while True:
                try:
                    img = self.server.read_frame()
                    try:
                        m = re.match('([\d]+)x([\d]+)', root)
                        if m:
                            size = int(m.group(1)), int(m.group(2))
                            img = cv2.resize(img, size)
                    except:
                        pass
                    for filter, params in filters.items():
                        try:
                            img = filter.apply(img, params)
                        except AttributeError:
                            pass
                    ret, jpg = cv2.imencode('.jpg', img)
                    if not ret:
                        raise RuntimeError('Could not encode img to JPEG')
                    jpg_bytes = jpg.tobytes()
                    self.wfile.write("--jpgboundary\r\n".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(jpg_bytes))
                    self.end_headers()
                    self.wfile.write(jpg_bytes)
                    time.sleep(self.server.read_delay)
                except (IOError, ConnectionError):
                    break
        elif filename.endswith(('.html', '.htm')):
            self.send_response(http.client.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            src = dirpath
            if ext:
                src += root
            src += '.mjpg'
            if parsed_url.query:
                src += '?' + parsed_url.query
            self.wfile.write(self.get_html(img_src=src).encode())
        else:
            self.send_response(http.client.NOT_FOUND)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_404_page.encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPSAuthServer):
    """Handle requests in a separate thread."""
    def __init__(self, capture_path, server_address, fps,
                 RequestHandlerClass, bind_and_activate=True):
        HTTPSAuthServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        ThreadingMixIn.__init__(self)
        try:
            capture_path = int(capture_path)
        except (TypeError, ValueError):
            pass
        self._capture_path = capture_path
        self._lock = threading.Lock()
        self._camera = cv2.VideoCapture()
        self.fps = fps

    def open_video(self):
        if not self._camera.open(self._capture_path):
            raise IOError('Could not open Camera {}'.format(self._capture_path))
        if self.fps is None:
            self.fps = self._camera.get(cv2.CAP_PROP_FPS)
            if self.fps == 0:
                self.fps = 30
        self.read_delay = 1. / self.fps

    def read_frame(self):
        with self._lock:
            ret, img = self._camera.read()
            if not ret:
                self.open_video()
                ret, img = self._camera.read()
        return img

    def serve_forever(self, poll_interval=0.5):
        self.open_video()
        try:
            super().serve_forever(poll_interval)
        except KeyboardInterrupt:
            self._camera.release()

def serve_https(path, address, port, users, passwords, keys,
                servercert, cacert, fps, HandlerClass=CamHandler):
    server = ThreadedHTTPServer(path,  (address, port), fps, HandlerClass)
    server.set_auth(users, passwords, keys)
    server.set_certs(servercert, cacert)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HTTPS Motion JPEG streaming server with OpenCV')
    parser.add_argument('path', help='camera number or filepath or url')
    parser.add_argument('port', nargs='?', type=int, default=8000)
    parser.add_argument('-a', '--address', default='')
    parser.add_argument('-u', '--users', nargs='*')
    parser.add_argument('-p', '--passwords', nargs='*')
    parser.add_argument('-k', '--keys', nargs='*')
    parser.add_argument('-s', '--servercert')
    parser.add_argument('-c', '--cacert')
    parser.add_argument('-f', '--fps', type=float)
    args = parser.parse_args()

    serve_https(args.path, args.address, args.port, args.users, args.passwords,
                args.keys, args.servercert, args.cacert, args.fps)
