# CVStreamer

HTTPS Motion JPEG streaming server for Python3 with OpenCV.

## Requirements
* [OpenCV](https://github.com/opencv/opencv)
* [SimpleHTTPSAuthServer](https://github.com/oza6ut0ne/SimpleHTTPSAuthServer)

## Usage

### Quick start

```sh
# Use camera 0.
$ python streamer.py 0
```

then, access [http://localhost:8000/cam.html](http://localhost:8000/cam.html) (or [cam.mjpg](http://localhost:8000/cam.mjpg) to get Motion JPEG stream directly).

### Custom filters

For example, access [http://localhost:8000/cam.html?mot=25](http://localhost:8000/cam.html?mot=25) to apply motion detection filter.  

To create your own filter, add `your-filter-name.py` to [/filter](https://github.com/oza6ut0ne/CVStreamer/tree/master/filter) directory.   
And then, access `http://localhost:8000/cam.html?your-filter-name`.  
See existing [filters](https://github.com/oza6ut0ne/CVStreamer/tree/master/filter) for more details.

### More options

Run `python streamer.py -h` and see [SimpleHTTPSAuthServer](https://github.com/oza6ut0ne/SimpleHTTPSAuthServer) for more command line arguments.  
(e.g., serve HTTPS, enable Basic authentication, etc.)
