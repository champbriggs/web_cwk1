from django.db import models

# Create your models here.

class Professor(models.Model):
    code = models.CharField(max_length=5, unique = True)
    name = models.CharField(max_length=30)
    total_rating = models.IntegerField(default=0)
    totalnum_rating = models.IntegerField(default=0)

class Module(models.Model):
    code = models.CharField(max_length=5, unique = True)
    name = models.CharField(max_length=100)

class ProfessorModuleRating(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    total_rating = models.IntegerField(default=0)
    totalnum_rating = models.IntegerField(default=0)

class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    professor = models.ManyToManyField(Professor)
    year = models.CharField(max_length=4)
    SEM_CHOICES = [
    ('1', 'Semester 1'),
    ('2', 'Semester 2')
    ]
    semester = models.CharField(max_length=1, choices = SEM_CHOICES, default='Please Select One')
