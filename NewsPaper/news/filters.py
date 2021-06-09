from django_filters import FilterSet
from .models import Post


# создаём фильтр
class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'preview_name': ['icontains'],
            'dateCreation': ['gte'],
            'postAuthor__authorUser__first_name': ['exact'],
        }
