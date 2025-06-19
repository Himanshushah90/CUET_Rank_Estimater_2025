from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('submit/', views.submit_scores, name='submit_scores'),
    path('rankings/', views.view_rankings, name='view_rankings'),
    path('', views.submit_scores, name='home'),
    # path('api/combinations/<int:course_id>/', views.api_combinations, name='api_combinations'),
    # path('api/subjects/', views.api_subjects, name='api_subjects'),
    path('admin/', admin.site.urls),
    # path('', include('estimator.urls')),
]
