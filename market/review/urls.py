from django.urls import path

from review.views import AddReviewView

urlpatterns = [
    path('add/', AddReviewView.as_view(), name='add')
]
