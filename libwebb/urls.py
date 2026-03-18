from django.urls import path
from . import views

# Giving your app a namespace helps in large projects
app_name = 'libwebb' 

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/dashboard/', views.admindashboard, name='admindashboard'),
    path('adminlogin/',views.adminlogin,name='adminlogin'),
    path('login_view/', views.login_view, name='login_view'), 
    path('library/', views.library, name='library'),
    
    # Book Management (Standardized Slashes)
    path('book/add/', views.add_book, name='add_book'),
    path('book/update/', views.update_book, name='update_book'),
    path('book/delete/', views.delete_book, name='delete_book'),
    path('book/details/', views.get_book_details, name='get_book_details'),
    path('book/titles/', views.get_all_book_titles, name='get_all_titles'),
    
    path('logout/', views.logout_view, name='logout'),
]