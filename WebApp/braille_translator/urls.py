from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('translate/<int:pk>/', views.translate_document, name='translate_document'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/<int:pk>/delete/', views.delete_document, name='delete_document'),
    path('document/<int:pk>/download/', views.download_braille, name='download_braille'),
]
