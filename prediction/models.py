from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.postgres.fields import ArrayField

fs = FileSystemStorage(location=settings.MEDIA_ROOT)

class Detection(models.Model):
    detection_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    file = models.FileField(storage=fs, upload_to='uploads/')  # Stores uploaded files
    file_type = models.CharField(max_length=50)
    prediction = models.BooleanField()
    confidence_score = models.FloatField()
    detection_date = models.DateTimeField(auto_now_add=True)
    grad_cam = ArrayField(models.CharField(max_length=255), blank=True, default=list)

    def __str__(self):
        return f"Detection {self.detection_id} by {self.user.username}"

class History(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    prediction = models.ForeignKey('Detection', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History {self.id} for {self.user.username}"
