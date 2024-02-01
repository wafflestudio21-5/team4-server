def image_upload_path(instance, filename):
    return f'img/episode/{instance.episode.id}/{filename}'
