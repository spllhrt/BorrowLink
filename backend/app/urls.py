from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home_page, name='home'), 
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('signout/', views.signout_view, name='signout'),
    path('contact/', views.contact_page, name='contact'),
    path('about/', views.about_page, name='about'),

    # Dashboards
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin User Management (all in one page)
    path('admin/users/', views.admin_users, name='admin_users'),

    # Admin Item Management (all in one page)
    path('admin/items/', views.admin_items, name='admin_items'),

    # Borrowing System (User side under user/)
    path('user/items/browse/', views.browse_items, name='browse_items'),
    path('user/items/borrow/<int:item_id>/', views.borrow_request, name='borrow_request'),
    path('user/my-borrows/', views.my_borrows, name='my_borrows'),

    # Admin Borrow Management
    path('admin/borrows/', views.manage_borrows, name='manage_borrows'),
    path('admin/borrows/approve/<int:borrow_id>/', views.approve_borrow, name='approve_borrow'),
    path('admin/borrows/return/<int:borrow_id>/', views.return_item, name='return_item'),
    
    # User penalties
    path('user/penalties/', views.user_penalties, name='user_penalties'),
    path("user/profile/", views.user_profile, name="user_profile"),

    # Admin penalties
    path('admin/penalties/', views.admin_penalties, name='admin_penalties'),
    path("admin/reports/", views.admin_reports, name="admin_reports"),  
    path("borrows/<int:borrow_id>/update/", views.update_borrow_status, name="update_borrow_status"),

    
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # Admin action to cancel overdue borrow
    path('admin/borrows/cancel-overdue/<int:borrow_id>/', views.cancel_overdue, name='cancel_overdue'),


]
