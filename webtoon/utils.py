def image_upload_path(instance, filename):
    return f'img/episode/{instance.episode.pk}/{filename}'

def titleImage_upload_path(instance, filename):
    return f'titleImage/{instance.title}/{filename}'

def thumbnail_upload_path(instance, filename):
    return f'thumbnail/{instance.webtoon.title}/{instance.episodeNumber}/{filename}'