from dateutil import parser
import datetime, os, copy, string, random, json
import pathlib


class FileInformation:
    pdf_extensions = [".pdf"]
    image_extensions = [".gif",".icns",".ico",".iff",".jng",".jpeg",".jpg",".jfif",".svg",".png",".webp"]
    video_extensions = [".3g2",".3gp",".aaf",".asf",".avchd",".avi",".drc",".flv",".m2v",".m3u8",".m4p",".m4v",".mkv",".mng",".mov",".mp2",".mp4",".mpe",".mpeg",".mpg",".mpv",".mxf",".nsv",".ogg",".ogv",".qt",".rm",".rmvb",".roq",".svi",".vob",".webm",".wmv",".yuv"]
    audio_extensions = [".wav",".bwf",".raw",".aiff",".flac",".m4a",".pac",".tta",".wv",".ast",".aac",".mp2",".mp3",".mp4",".amr",".s3m",".3gp",".act",".au",".dct",".dss",".gsm",".m4p",".mmf",".mpc",".ogg",".oga",".opus",".ra",".sln",".vox"]

def getattrkey(__o,__name):
    if type(__o) == dict:
        return __o.get(__name)
    else:
        if not hasattr(__o,__name):
            return None
        return getattr(__o,__name)
    
def setattrkey(__o,__name,__value = None):
    if type(__o) == dict:
        __o[__name] = __value
    else:
        setattr(__o,__name,__value)
    return __o

def parse_date(s,**kwargs):
    try:
        return parser.parse(s,**kwargs)
    except:
        return s

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

