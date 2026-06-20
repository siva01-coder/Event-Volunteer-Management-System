from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'),
         name='home'),
    path('accounts/', include('accounts.urls')),
    path('events/', include('events.urls')),
]
