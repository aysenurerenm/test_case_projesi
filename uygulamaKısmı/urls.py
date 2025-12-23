from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('llm-test/', views.llm_testcode, name='llm_testcode'),
     path('metrics/', views.metrics, name="metrics"),
    path('graph/', views.graph, name="graph"),
    path('rl-cover/', views.rl_cover, name="rl_cover"),
]
