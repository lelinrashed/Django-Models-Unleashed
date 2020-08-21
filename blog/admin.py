from blog.models import PostModel
from django.contrib import admin

# Register your models here.


class PostModelAdmin(admin.ModelAdmin):
    fields = [
        'title',
        'content',
        'publish',
        'publish_date',
        'active',
        'updated',
        'timestamp',
        'get_age'
    ]
    readonly_fields = ['updated', 'timestamp', 'get_age']

    def get_age(self, obj, *args, **kwargs):
        return str(obj.age)

    class Meta:
        model = PostModel


admin.site.register(PostModel, PostModelAdmin)
