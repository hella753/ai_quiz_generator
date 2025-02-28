import django_filters
from quiz_app.models import Quiz


class QuizFilter(django_filters.FilterSet):
    """
    FilterSet for a Quiz model.
    """
    creator = django_filters.CharFilter(field_name="creator__username")
    taker = django_filters.CharFilter(
        field_name='questions__your_answers__user__username',
        lookup_expr='exact'
    )

    class Meta:
        model = Quiz
        fields = ['creator', 'taker']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.distinct()
