from django.shortcuts import redirect
from django.views import View

from review.models import Review


class AddReviewView(View):
    def post(self, request):
        review_text = request.POST.get('review')
        product_id = request.POST.get('product')
        if review_text:
            Review.objects.create(review_text=review_text,
                                  user=request.user,
                                  product_id=product_id)
        return redirect('products:detail', product_id)
