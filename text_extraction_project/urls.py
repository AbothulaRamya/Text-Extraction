"""text_extraction_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from video_text_recognition import views  # Import your app's views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('video/', include('video_text_recognition.urls')),  # Ensure 'video_text_recognition/urls.py' exists
    #path('process-image/', views.process_image_view, name='process_image'),  
]

# Serve media files only in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
