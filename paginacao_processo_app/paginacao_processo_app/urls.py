from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('carimbar_processo/', views.carimbar_pdf, name='carimbar_processo'),
    path(' ', views.carimbar_pdf, name='carimbar_processo'),
    path('', views.carimbar_pdf, name='carimbar_pdf')
]