from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('profile/edit/', views.Edit.as_view(), name='edit'),

    path('change-password/',
         views.ChangePassword.as_view(),
         name='password_change'),

    path('reset-password/',
         views.PasswordReset.as_view(),
         name='password_reset'),

    path('reset-password/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),

    path('reset-password/<slug:uidb64>/<slug:token>/',
         views.PasswordResetConfirm.as_view(),
         name='password_reset_confirm'),
]
