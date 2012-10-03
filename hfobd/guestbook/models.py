import datetime
from django.db import models
import pytz

class Guest(models.Model):
    email_address = models.TextField()
    created = models.DateTimeField()

    @classmethod
    def Create(cls, email_address):
        g = Guest(email_address=email_address, created=datetime.datetime.now().replace(tzinfo=pytz.UTC))
        g.save()
        return g