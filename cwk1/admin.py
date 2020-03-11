from django.contrib import admin
from .models import Professor, Module, ProfessorModuleRating, ModuleInstance
# Register your models here.

admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ProfessorModuleRating)
admin.site.register(ModuleInstance)
