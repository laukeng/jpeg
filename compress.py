import glob
import os
import traceback
from PIL import ExifTags, Image


# WORK_DIR = '/storage/emulated/0/DCIM/Camera'
WORK_DIR = 'D:\\手机相册\\Sony Z1'
JPG_FILTER = os.path.join(WORK_DIR, '*.[jJ][pP][gG]')


def comprs_jpg(file):
    try:
        img = Image.open(file)
        exif = img.info['exif']
        img.save(file, exif=exif, quality=80)
        return os.path.getsize(file)
    except Exception as err:
        print(err)
        print(traceback.format_exc())
        return 0


def comprs_jpgs():
    filecount = 0
    filetotal = len(glob.glob(JPG_FILTER))
    compressed = set()
    list_file =  os.path.join(WORK_DIR, 'compressed.list')
    with open(list_file, mode='a+', encoding='utf-8') as f:
        f.seek(0)
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            compressed.add(line.split(',')[0])

        for file in glob.glob(JPG_FILTER):
            filecount += 1
            if os.path.split(file)[1] in compressed:
                print(os.path.split(file)[1], 'Already Compressed', '(%d/%d)' % (filecount, filetotal))
            else:
                filesize = os.path.getsize(file)
                new_size = comprs_jpg(file)
                f.write('%s,%d,%d\n' % (os.path.split(file)[1], filesize, new_size))
                print('%s %d --> %d (%d/%d)' % (os.path.split(file)[1], filesize, new_size, filecount, filetotal))


if __name__ == '__main__':
    comprs_jpgs()
