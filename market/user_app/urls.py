from django.urls import path

from .views import (AccountView, HistoryView, LogIn, LogOut, SignUp,
                    UpdateProfileInfo)

urlpatterns = [
    path("", AccountView.as_view(), name="account"),
    path("login/", LogIn.as_view(), name="login"),
    path("logout/", LogOut.as_view(), name="logout"),
    path("register/", SignUp.as_view(), name="sign-up"),
    path("profile/", UpdateProfileInfo.as_view(), name="profile"),
    path("history/", HistoryView.as_view(), name="history"),
]
