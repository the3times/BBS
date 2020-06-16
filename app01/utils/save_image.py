import os, uuid, time
from BBS import settings


def save_image(file_obj):
    file_dir = os.path.join(settings.BASE_DIR, 'media', 'images')
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
    file_format = file_obj.name.rsplit('.', maxsplit=1)[-1]
    file_new_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(time.time())))
    file_new_name = '.'.join([file_new_name, file_format])
    file_naw_path = os.path.join(settings.BASE_DIR, 'media', 'images', file_new_name)

    with open(file_naw_path, 'wb') as f:
        for line in file_obj:
            f.write(line)

    return file_naw_path, file_new_name