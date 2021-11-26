from django.contrib import admin

# Register your models here.
from .models import User, Chaves
admin.site.register(User)
admin.site.register(Chaves)

