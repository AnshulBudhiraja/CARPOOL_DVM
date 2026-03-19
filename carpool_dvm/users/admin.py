from django.contrib import admin
from .models import User, Driver
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # This tells Django: "Just show the text, don't try to make it a form field!"
    readonly_fields = ('last_login', 'date_joined')

admin.site.register(Driver)