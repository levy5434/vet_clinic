from django.urls import path
from . import views

app_name='app'
urlpatterns = [
    path('', views.index, name='index'),
    path('animals/',views.animals, name='animals'),
    path('animals/<int:animal_id>/disease/',views.disease,name='disease'),
    path('animals/disease/<int:disease_id>',views.check_disease,name='check_disease'),
    path('browse_clients/',views.browse_clients,name='browse_clients'),
    path('browse_clients/<int:client_id>/',views.client,name='client'),
    path('browse_clients/<int:client_id>/add_pet/',views.add_pet,name='add_pet'),
    path('browse_clients/pet/<int:pet_id>',views.pet,name='pet'),
    path('browse_clients/pet/delete_pet/<int:pet_id>/', views.pet_delete,name='pet_delete'),
    path('browse_clients/pet/<int:pet_id>/add_disease',views.add_disease,name='add_disease'),
    path('browse_clients/disease/<int:disease_id>/',views.pet_disease,name='pet_disease'),
    path('browse_clients/medicine/delete_medicine/<int:medicine_id>/', views.medicine_delete,name='medicine_delete'),
    path('browse_clients/disease/delete_disease/<int:disease_id>/', views.disease_delete,name='disease_delete'),
    path('browse_clients/disease/<int:disease_id>/add_medicine/',views.add_medicine,name='add_medicine'),
    path('browse_clients/disease/edit_medicine/<int:medicine_id>/',views.edit_medicine,name='edit_medicine'),
    path('browse_clients/disease/edit_disease/<int:disease_id>/',views.edit_disease,name='edit_disease'),
]