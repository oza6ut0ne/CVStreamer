import cv2
import http
import importlib
import os
import re
import sys
import threading
import time
import urllib
from collections import OrderedDict
from SimpleHTTPSAuthServer import ThreadedHTTPSAuthServer, AuthHandler

class CamHandler(AuthHandler):
    def __init__(self, request, client_address, server):
        self.html_404_page = '<h1>NOT FOUND</h1>'
        self.boundary = '--jpgboundary'
        super().__init__(request, client_address, server)

    def get_html(self, img_src='cam.mjpg'):
        return '<img src="{}"/>'.format(img_src)

    def parse_ordered_qs(self, qs, keep_blank_values=False, strict_parsing=False,
                         encoding='utf-8', errors='replace'):
        parsed_result = OrderedDict()
        pairs = urllib.parse.parse_qsl(qs, keep_blank_values, strict_parsing,
                                       encoding=encoding, errors=errors)
        for name, value in pairs:
            if name in parsed_result:
                parsed_result[name].append(value)
            else:
                parsed_result[name] = [value]
        return parsed_result

    def do_GET(self):
        if not super().do_GET():
            return

        parsed_url = urllib.parse.urlparse(self.path)
        dirpath, filename = os.path.split(parsed_url.path)
        query = self.parse_ordered_qs(parsed_url.query, keep_blank_values=True)
        root, ext = os.path.splitext(filename)

        if filename.endswith('.mjpg'):
            self.send_mjpg(query, root)
        elif filename.endswith(('.html', '.htm')):
            self.send_html(parsed_url, dirpath, query, root, ext)
        else:
            self.send_response(http.client.NOT_FOUND)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_404_page.encode())

    def send_html(self, parsed_url, dirpath, query, root, ext):
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

    def send_mjpg(self, query, root):
        self.send_response(http.client.OK)
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=' + self.boundary)
        self.end_headers()
        filters = {}
        for key in query:
            module_name = 'filter.' + key
            try:
                sys.dont_write_bytecode = True
                filter_module = importlib.import_module(module_name)
                filter = filter_module.Filter(query[key])
                filters[filter] = os.stat(filter_module.__file__)
            except ModuleNotFoundError as e:
                print(e)
            except AttributeError as e:
                sys.modules.pop(module_name)
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

                new_filters = {}
                for filter in filters:
                    try:
                        module = sys.modules[filter.__module__]
                        stat = os.stat(module.__file__)
                        if filters[filter] != stat:
                            sys.dont_write_bytecode = True
                            module = importlib.reload(module)
                            filter = module.Filter(filter.params)
                            sys.dont_write_bytecode = False
                        new_filters[filter] = stat
                        img = filter.apply(img)
                    except FileNotFoundError as e:
                        print(e)
                    except ModuleNotFoundError as e:
                        print(e)
                    except AttributeError as e:
                        print(e)
                filters = new_filters
                ret, jpg = cv2.imencode('.jpg', img)
                if not ret:
                    raise RuntimeError('Could not encode img to JPEG')
                jpg_bytes = jpg.tobytes()
                self.wfile.write((self.boundary + '\r\n').encode())
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length', len(jpg_bytes))
                self.end_headers()
                self.wfile.write(jpg_bytes)
                time.sleep(self.server.read_delay)
            except (IOError, ConnectionError):
                break


class CamServer(ThreadedHTTPSAuthServer):
    """Handle requests in a separate thread."""
    def __init__(self, capture_path, server_address, fps,
                 RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
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

def serve_https(path, bind, port, users, passwords, keys,
                servercert, cacert, fps, HandlerClass=CamHandler):
    server = CamServer(path, (bind, port), fps, HandlerClass)
    server.daemon_threads = True
    server.set_auth(users, passwords, keys)
    server.set_certs(servercert, cacert)
    server.serve_forever()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HTTPS Motion JPEG streaming server with OpenCV')
    parser.add_argument('path', help='camera number or filepath or url')
    parser.add_argument('port', nargs='?', type=int, default=8000)
    parser.add_argument('-b', '--bind', default='', metavar='ADDRESS')
    parser.add_argument('-u', '--users', nargs='*')
    parser.add_argument('-p', '--passwords', nargs='*')
    parser.add_argument('-k', '--keys', nargs='*')
    parser.add_argument('-s', '--servercert')
    parser.add_argument('-c', '--cacert')
    parser.add_argument('-f', '--fps', type=float)
    args = parser.parse_args()

    serve_https(args.path, args.bind, args.port, args.users, args.passwords,
                args.keys, args.servercert, args.cacert, args.fps)
