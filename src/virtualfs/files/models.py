from django.db import models

class Folder(models.Model):
    """Représente un dossier pouvant contenir des fichiers ou d'autres dossiers."""
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class File(models.Model):
    """Représente un fichier stocké dans un dossier."""
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # Peut être utilisé pour les fichiers texte simples

    # Nouveau champ pour les fichiers réels (PDF, images, etc.)
    file = models.FileField(upload_to='files/', null=True, blank=True)

    def __str__(self):
        return self.name

class Bookmark(models.Model):
    """Représente un favori (lien)."""
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.title
