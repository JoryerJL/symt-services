from django.db import models

from common.models import CommonBaseModel


class Organization(CommonBaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
