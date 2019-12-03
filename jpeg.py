import datetime
import glob
import os
import re
import traceback
import piexif
from PIL import ExifTags, Image


# WORK_DIR = '/storage/emulated/0/DCIM/Camera'
WORK_DIR = 'D:\\手机相册\\Sony Z1'
JPG_FILTER = os.path.join(WORK_DIR, '*.[jJ][pP][gG]')
BAD_TIME = ['2002:12:08 12:00:00']


def get_exif_time(file):
    img = Image.open(file)
    date_time = ''
    try:
        exif = {
            ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in ExifTags.TAGS
        }
        date_time = exif['DateTime']
    except Exception as err:
        print(err)
        print(traceback.format_exc())
    date_time = date_time.replace(':', '').replace(' ', '_').strip()
    return date_time


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


def rename_jpg(file, date_time):
    new_name = 'IMG_' + date_time + '.jpg'
    new_name = os.path.join(WORK_DIR, new_name)
    i = 1
    while os.path.exists(new_name):
        if file.lower() == new_name.lower():
            return 'Not Renamed'
        new_name = 'IMG_' + date_time + '_' + str(i) + '.jpg'
        new_name = os.path.join(WORK_DIR, new_name)
        i += 1
    try:
        os.rename(file, new_name)
    except Exception as err:
        print(err)
        print(traceback.format_exc())
        return 'ERROR'
    return os.path.split(new_name)[1]


def rename_jpgs():
    filecount = 0
    filetotal = len(glob.glob(JPG_FILTER))
    for file in glob.glob(JPG_FILTER):
        filecount += 1
        date_time = get_exif_time(file)
        if date_time == '':
            print(os.path.split(file)[1], 'No Exif Date', '(%d/%d)' % (filecount, filetotal))
        else:
            new_name = rename_jpg(file, date_time)
            print(os.path.split(file)[1], '-->', new_name, '(%d/%d)' % (filecount, filetotal))


def zip_jpg(file):
    try:
        img = Image.open(file)
        exif = img.info['exif']
        img.save(file, exif=exif, quality=80)
        return os.path.getsize(file)
    except Exception as err:
        print(err)
        print(traceback.format_exc())
        return 0


def zip_jpgs():
    filecount = 0
    filetotal = len(glob.glob(JPG_FILTER))
    zipped = set()
    list_file =  os.path.join(WORK_DIR, 'zipped.list')
    with open(list_file, mode='a+', encoding='utf-8') as f:
        f.seek(0)
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            zipped.add(line.split(',')[0])


        for file in glob.glob(JPG_FILTER):
            filecount += 1
            if os.path.split(file)[1] in zipped:
                print(os.path.split(file)[1], 'Already Zipped', '(%d/%d)' % (filecount, filetotal))
            else:
                filesize = os.path.getsize(file)
                new_size = zip_jpg(file)
                f.write('%s,%d,%d\n' % (os.path.split(file)[1], filesize, new_size))
                print('%s %d --> %d (%d/%d)' % (os.path.split(file)[1], filesize, new_size, filecount, filetotal))


# fix_exifs()
# rename_jpgs()
# zip_jpgs()
