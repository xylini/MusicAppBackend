from django.contrib import admin
from api import models


@admin.register(models.Song)
class SongAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SongStat)
class SongStatAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Level)
class LevelAdmin(admin.ModelAdmin):
    pass
