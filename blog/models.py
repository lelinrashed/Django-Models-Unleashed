from datetime import datetime, timedelta

from blog.validators import validate_author_email, validate_rashed
from django.db import models

# Create your models here.
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timesince import timesince

PUBLISH_CHOICES = [
    ('draft', 'Draft'),
    ('publish', 'Publish'),
    ('private', 'Private'),
]


class PostModelQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class PostModelManager(models.Manager):
    def get_queryset(self):
        return PostModelQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        qs = super(PostModelManager, self).all(*args, **kwargs).active()   #.filter(active=True)
        print(qs)
        return qs


class PostModel(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=240,
                             verbose_name='Post Title',
                             unique=True,
                             error_messages={
                                 "unique": "This title is not unique, Please try another.",
                                 "blank": "This field should not be empty. Fill it"
                             },
                             help_text="Must be a unique title."
                             )
    slug = models.SlugField(null=True, blank=True, editable=False)
    content = models.TextField(null=True, blank=True)
    publish = models.CharField(max_length=120, choices=PUBLISH_CHOICES, default='draft')
    view_count = models.IntegerField(default=0)
    publish_date = models.DateField(auto_now=False, auto_now_add=False, default=timezone.now)
    author_email = models.EmailField(max_length=240, null=True, blank=True, validators=[validate_rashed])
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PostModelManager()
    other = PostModelManager()


    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = slugify(self.title)
        super(PostModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        # unique_together = [('title', 'slug')]

    def __str__(self):
        return self.title

    @property
    def age(self):
        if self.publish == 'publish':
            now = timezone.now()
            publish_time = datetime.combine(self.publish_date, datetime.now().min.time())
            try:
                difference = now - publish_time
            except:
                return "Unknown"

            if difference <= timedelta(minutes=1):
                return "Just now"
            return "{time} ago".format(time=timesince(publish_time).split(', ')[0])
        return 'Not publish'


def blog_post_model_pre_save_receiver(sender, instance, *args, **kwargs):
    print('Pre Save')
    if not instance.slug:
        instance.slug = slugify(instance.title)
        instance.save()


pre_save.connect(blog_post_model_pre_save_receiver, sender=PostModel)


def blog_post_model_post_save_receiver(sender, instance, created, *args, **kwargs):
    print('After save')
    if not instance.slug:
        instance.slug = slugify(instance.title)
        instance.save()


post_save.connect(blog_post_model_post_save_receiver, sender=PostModel)
