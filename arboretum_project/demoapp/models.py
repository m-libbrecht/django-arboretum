from mptt.models import  MPTTModel
from django.db import models
from django.core.urlresolvers import reverse

class Domain(MPTTModel):

    parent = models.ForeignKey('self',  null=True, blank=True, related_name='children')
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'domains'

    class MPTTMeta:
        order_insertion_by = ['title']

