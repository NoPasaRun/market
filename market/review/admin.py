from django.contrib import admin

from review.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'shrink_review_text', 'added_at', ]
    ordering = ['id', 'user', 'added_at', ]
    list_filter = ['user']

    def shrink_review_text(self, obj):
        return f'{obj.review_text[:15]}...' if len(obj.review_text) >= 15 else obj.review_text
