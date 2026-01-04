from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('translate/<int:pk>/', views.translate_document, name='translate_document'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/<int:pk>/delete/', views.delete_document, name='delete_document'),
    path('document/<int:pk>/download/', views.download_braille, name='download_braille'),
    
    # Braille image routes
    path('braille-image/', views.braille_image_upload, name='braille_image_upload'),
    path('braille-image/<int:pk>/translate/', views.translate_braille_image, name='translate_braille_image'),
    path('braille-image/<int:pk>/', views.braille_image_detail, name='braille_image_detail'),
    path('braille-image/<int:pk>/delete/', views.delete_braille_image, name='delete_braille_image'),
]

