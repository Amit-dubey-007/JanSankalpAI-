from django.urls import path
from . import views

app_name = "complaints"

urlpatterns=[
    path('create-complaint/',views.create_complaint,name='create_complaint'),
    path('mycomplaints/',views.mycomplaints,name='mycomplaints'),
    path('mycomplaints/<int:pk>/', views.mycomplaint_detail, name='mycomplaint_detail'),
    path('mycomplaints/<int:pk>/delete/confirm/', views.delete_complaint, name='confirm_delete_complaint'),
    path('',views.public_dashboard,name='public_dashboard'),
    path('complaints/<int:pk>/support/', views.toggle_support, name='toggle_support'),
    path('complaints/<int:pk>/comment/', views.comment_view, name='comment'),
    path('complaints/<int:pk>/follow/', views.toggle_follow, name='toggle_follow'),
    path('complaints/<int:pk>/', views.complaint_public_detail, name='complaint_public_detail'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/',views.open_notification,name="open_notification"),
    path('notifications/mark-all-read/',views.mark_all_read,name="mark_all_read"),
    path('faq',views.faq,name='faq'),
    path('govt-dashboard',views.govt_dashboard,name='govt_dashboard'),
    path('govt-complaint-view/<int:pk>',views.govt_detail_complaint,name='govt_detail_complaint'),
    path("complaint/<int:pk>/delete-comment/",views.delete_comment,name="delete_comment"),
    path("complaint/<int:pk>/change-status/",views.change_complaint_status,name="change_complaint_status"),
    path("manage-officials/",views.manage_officials,name="manage_officials",),
    path("make-government/<int:user_id>/",views.make_government,name="make_government"),
    path("remove-government/<int:user_id>/",views.remove_government,name="remove_government"),
    path("guidelines",views.guidelines,name="guidelines"),
    path("contact",views.contact,name="contact"),
    path('about',views.about,name="about"),
    path('test-email',views.test_email,name="test_email"),
    path('test-socket',views.test_socket,name="test_socket"),
]