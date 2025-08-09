from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('classify/', views.classify_email_view, name='classify_email'),
    path('feedback/<int:classification_id>/', views.submit_feedback, name='submit_feedback'),
]