import datetime
import glob
import os
import re
import traceback
import piexif
from PIL import ExifTags, Image


# WORK_DIR = '/storage/emulated/0/DCIM/Camera'
# WORK_DIR = 'D:\\Pictures\\Sony Z1'
WORK_DIR = os.path.dirname(__file__)
JPG_FILTER = os.path.join(WORK_DIR, '*.[jJ][pP][gG]')
BAD_TIME = ['2002:12:08 12:00:00']


def fix_exif_time(file):
    pattern = r'\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2}'
    exif_dict = {}
    try:
        exif_dict = piexif.load(file)
        if 41729 in exif_dict['Exif']:
            exif_dict['Exif'][41729] = b'1'
    except Exception as err:
        print(err)
        print(traceback.format_exc())
        return 'LOAD ERROR'
                
    date_time = ''
    if '0th' in exif_dict:
        if 306 in exif_dict['0th']:
            date_time = exif_dict['0th'][306].decode()
            print('Read From 0th', date_time)
            if re.search(pattern, date_time) and date_time not in BAD_TIME:
                return 'Unmodified'
        else:
            exif_dict['0th'][306] = b''
    else:
        exif_dict['0th'] = {}
        exif_dict['0th'][306] = b''

    if re.search(pattern, date_time) is None or date_time in BAD_TIME:
        if 'GPS' in exif_dict and 29 in exif_dict['GPS'] and 7 in exif_dict['GPS']:
            gps_h = exif_dict['GPS'][7][0][0]
            gps_m = exif_dict['GPS'][7][1][0]
            gps_s = int(exif_dict['GPS'][7][2][0]/exif_dict['GPS'][7][2][1])
            if 0 <= gps_h <= 24 and 0<= gps_m <= 60 and 0 <= gps_s <= 60:
                gps_time = str(str(gps_h) + ':' + str(gps_m) + ':' + str(gps_s))
            else:
                gps_time = '00:00:00'
            date_time = exif_dict['GPS'][29].decode() + ' ' + gps_time
            utc_date = datetime.datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
            local_date = utc_date + datetime.timedelta(hours=8)
            date_time = datetime.datetime.strftime(local_date, '%Y:%m:%d %H:%M:%S')
            print('Read From GPS', date_time)

    if re.search(pattern, date_time) is None or date_time in BAD_TIME:
        if 'Exif' in exif_dict and 36867 in exif_dict["Exif"]:
            date_time = exif_dict["Exif"][36867].decode()
            print('Read From Exif', date_time)
            
    if re.search(pattern, date_time) is None or date_time in BAD_TIME:
        pattern2 = r'(\d{4})[\-\:\s\_\/]?(1[0-2]|0[1-9])[\-\:\s\_\/]?([1-2]\d|3[0-1]|0[1-9])'
        pattern2 += r'[\-\:\s\_\/]?([0-1]\d|2[0-4])[\-\:\s\_\/]?([0-5]\d)[\-\:\s\_\/]?([0-5]\d)'
        find = re.search(pattern2, os.path.split(file)[1])
        if find:
            date_time = '%s:%s:%s %s:%s:%s' % find.groups()
            print('Read From FileName', date_time)

    if re.search(pattern, date_time) and date_time not in BAD_TIME:
        date_time = bytes(date_time, encoding="ascii")
        exif_dict["Exif"][36867] = date_time
        exif_dict["Exif"][36868] = date_time
        exif_dict["0th"][306] = date_time
        try:
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, file)
        except Exception as err:
            print(os.path.split(file)[1], 'Save ERROR!', err)
            print(traceback.format_exc())
            if str(err) == "Given data isn't JPEG.":
                print('Del thumbnail')
                del exif_dict['thumbnail']
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, file)
    
    return str(os.path.getsize(file))
    

def fix_exifs():
    filecount = 0
    filetotal = len(glob.glob(JPG_FILTER))
    for file in glob.glob(JPG_FILTER):
        filesize = os.path.getsize(file)
        filecount += 1
        new_size = fix_exif_time(file)
        print(os.path.split(file)[1], filesize, '-->', new_size, '(%d/%d)' % (filecount, filetotal))


if __name__ == '__main__':
    fix_exifs()
