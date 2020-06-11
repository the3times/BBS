from django.contrib import admin

from app01 import models


admin.site.register(models.UserInfo)
admin.site.register(models.Blog)
admin.site.register(models.Tag)
admin.site.register(models.Category)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)
admin.site.register(models.UpDown)
admin.site.register(models.Comment)
