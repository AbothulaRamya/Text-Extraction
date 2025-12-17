from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from video_text_recognition import views  # Import your app views

urlpatterns = [
    path('', views.home, name='home'),  
    path('video/upload_video/', views.upload_video, name='upload_video'),
] 

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
