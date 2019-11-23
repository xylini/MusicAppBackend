from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class Song(models.Model):
    SHORT = 'Short'
    MEDIUM = 'Medium'
    LONG = 'Long'

    CHOICES = (
        (SHORT, SHORT),
        (MEDIUM, MEDIUM),
        (LONG, LONG)
    )

    name = models.CharField(max_length=250)
    file = models.FileField(upload_to='songs/')
    length = models.CharField(max_length=250, choices=CHOICES)
    level = models.ForeignKey('Level', on_delete=models.CASCADE)


class Level(models.Model):
    name = models.CharField(max_length=250)


class SongStat(models.Model):
    practice_time = models.PositiveIntegerField()
    high_score = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
