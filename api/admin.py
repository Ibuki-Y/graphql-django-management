from django.contrib import admin
from .models import Employee, Department

# admin(Dashboard)にモデルを登録
admin.site.register(Employee)
admin.site.register(Department)
