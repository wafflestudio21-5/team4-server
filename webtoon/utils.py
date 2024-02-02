def image_upload_path(instance, filename):
    return f'img/episode/{instance.episode.id}/{filename}'

def titleImage_upload_path(instance, filename):
    return f'titleImage/{instance.id}/{filename}'

def thumbnail_upload_path(instance, filename):
    return f'thumbnail/{instance.id}/{filename}'