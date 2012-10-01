import datetime
from django.db import models
import pytz

class SavedInsight(models.Model):
    image_id = models.CharField(max_length=1024)
    title = models.TextField()
    author = models.TextField()
    data = models.TextField(default='')
    visible = models.BooleanField()
    created = models.DateTimeField()

    @classmethod
    def Create(cls, image_id, title, author, data):
        saved_insight = SavedInsight(
            image_id=image_id,
            title=title,
            author=author,
            data=data,
            visible=False,
            created=datetime.datetime.now().replace(tzinfo=pytz.UTC))
        saved_insight.save()
        return saved_insight

    @classmethod
    def SetAsVisible(cls, image_id):
        saved_insight = SavedInsight.objects.get(image_id=image_id)
        saved_insight.visible = True
        saved_insight.save()

    @classmethod
    def SetAsInvisible(cls, image_id):
        saved_insight = SavedInsight.objects.get(image_id=image_id)
        saved_insight.visible = False
        saved_insight.save()

    @classmethod
    def Gallery(cls):
        return SavedInsight.objects.filter(visible=True).order_by('-created')
