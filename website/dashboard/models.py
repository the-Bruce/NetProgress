import math
import string
import random

from django.db import models


# Create your models here.
def new_key():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(128))


class Project(models.Model):
    user = models.ForeignKey('accounts.Member', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    apikey = models.CharField(max_length=128, default=new_key)


class Run(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    apikey = models.CharField(max_length=128, default=new_key)
    start_date = models.DateTimeField(auto_now_add=True)


class Bar(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    maxval = models.IntegerField()
    current = models.IntegerField()
    name = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)
    errored = models.BooleanField(default=False)

    @property
    def percent(self):
        return math.floor((self.current / self.maxval) * 100)
