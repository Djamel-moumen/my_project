from django.urls import path
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path('', views.landing),
    path('myDatasets/', views.DatasetsListView.as_view()),
    path('<int:pk>/delete/', views.DatasetDeleteView.as_view()),
    path('processing/<int:id>/', TemplateView.as_view(template_name='core/processing_page.html')),
]

