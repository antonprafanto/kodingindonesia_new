from django.urls import path

from . import views


app_name = "learning"

urlpatterns = [
    path("", views.home, name="home"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:slug>/learn/", views.course_learn, name="course_learn"),
    path("courses/<slug:slug>/quiz/<int:quiz_id>/", views.quiz_detail, name="quiz_detail"),
    path("courses/<slug:slug>/certificate/", views.certificate_view, name="certificate"),
    path("instructor/dashboard/", views.instructor_dashboard, name="instructor_dashboard"),
    path("instructor/courses/create/", views.course_create, name="course_create"),
    path("instructor/courses/<slug:slug>/edit/", views.course_edit, name="course_edit"),
    path("instructor/courses/<slug:slug>/delete/", views.course_delete, name="course_delete"),
    path("instructor/courses/<slug:slug>/lessons/add/", views.lesson_create, name="lesson_create"),
    path(
        "instructor/courses/<slug:slug>/lessons/<int:lesson_id>/edit/",
        views.lesson_edit,
        name="lesson_edit",
    ),
    path(
        "instructor/courses/<slug:slug>/lessons/<int:lesson_id>/delete/",
        views.lesson_delete,
        name="lesson_delete",
    ),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
]