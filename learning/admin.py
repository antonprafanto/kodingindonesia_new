from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    User,
    Category,
    Tag,
    Course,
    Lesson,
    Quiz,
    Question,
    Choice,
    Enrollment,
    LessonProgress,
    QuizSubmission,
    QuizAnswer,
    Comment,
    Review,
    Certificate,
    Notification,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Profil", {"fields": ("role", "bio", "avatar")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "category", "level", "is_published", "created_at")
    list_filter = ("category", "level", "is_published")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_preview")
    list_filter = ("course",)
    ordering = ("course", "order")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_final", "created_at")
    list_filter = ("course", "is_final")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz",)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("question", "is_correct")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "is_completed")
    list_filter = ("course", "is_completed")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "is_completed", "completed_at")
    list_filter = ("is_completed",)


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "enrollment", "score", "is_passed", "submitted_at")
    list_filter = ("quiz", "is_passed")


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("submission", "question", "selected_choice", "is_correct")
    list_filter = ("is_correct",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "created_at")
    list_filter = ("course", "user")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rating", "created_at")
    list_filter = ("course", "rating")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "code", "issued_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "created_at", "is_read")
    list_filter = ("is_read",)