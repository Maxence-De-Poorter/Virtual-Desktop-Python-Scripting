# gallery/models.py

from django.db import models

class GalleryImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/')

    def __str__(self):
        return self.title or "Image sans titre"
