from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
class Document(models.Model):
    title = models.CharField(
        "Заголовок",
        max_length=256
    )
    description = models.TextField("Описание")
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="documents"
    )
    doc_date = models.DateTimeField(
        "Дата оригинального документа",
        help_text="Дата оригинального документа"
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "документы"
        verbose_name_plural = "Документы"
        ordering = ('-doc_date',)

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        images = self.photos.all()
        for photo in images:
            photo.image.delete(save=True)
            photo.image.delete()
        super().delete()


class DocumentPhoto(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name='Документ',
        related_name='photos'
    )
    image = models.ImageField('Фото', upload_to='document_images', blank=False)

    class Meta:
        verbose_name = "фото"
        verbose_name_plural = "Фотографии"
        ordering = ('-id',)

    def __str__(self):
        return self.document.title
