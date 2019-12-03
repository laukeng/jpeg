import glob
import os
import traceback
from PIL import Image


# WORK_DIR = '/storage/emulated/0/DCIM/Camera'
WORK_DIR = 'D:\\Pictures\\Sony Z1'
JPG_FILTER = os.path.join(WORK_DIR, '*.[jJ][pP][gG]')


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


if __name__ == '__main__':
    rename_jpgs()
