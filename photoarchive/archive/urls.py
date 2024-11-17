from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, reverse_lazy
from .views import *
app_name = 'archive'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('document/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('document/create/', DocumentCreateView.as_view(), name='document_create'),
    path('document/<int:pk>/edit/', DocumentUpdateView.as_view(), name='document_edit'),
    path('document/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
    path('download/<int:document_pk>/<int:image_pk>', download_document, name='document_download'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
