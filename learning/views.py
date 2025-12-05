from __future__ import annotations

import uuid

from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail

from .forms import UserRegistrationForm, CourseForm, LessonForm, CommentForm, ReviewForm
from .models import (
    User,
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
)


def home(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "")
    courses = Course.objects.filter(is_published=True).select_related("instructor", "category")
    if query:
        courses = courses.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
        )
    courses = courses.annotate(num_enrollments=Count("enrollments")).order_by("-created_at")[:8]
    categories = (
        Course.objects.filter(is_published=True)
        .values("category__id", "category__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    context = {
        "courses": courses,
        "categories": categories,
        "query": query,
    }
    return render(request, "learning/home.html", context)


def course_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "")
    category_id = request.GET.get("category")
    courses = Course.objects.filter(is_published=True).select_related("instructor", "category")

    if query:
        courses = courses.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
        )
    if category_id:
        courses = courses.filter(category_id=category_id)

    courses = courses.annotate(num_enrollments=Count("enrollments")).order_by("-created_at")
    categories = (
        Course.objects.filter(is_published=True)
        .values("category__id", "category__name")
        .annotate(total=Count("id"))
        .order_by("category__name")
    )

    context = {
        "courses": courses,
        "categories": categories,
        "selected_category": category_id,
        "query": query,
    }
    return render(request, "learning/course_list.html", context)


def course_detail(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(
        Course.objects.select_related("instructor", "category").prefetch_related(
            "tags", "lessons", "reviews", "comments__user"
        ),
        slug=slug,
        is_published=True,
    )

    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login untuk melanjutkan.")
            return redirect("login")

        if "enroll" in request.POST:
            if enrollment:
                messages.info(request, "Anda sudah terdaftar di kursus ini.")
            else:
                enrollment = Enrollment.objects.create(course=course, student=request.user)
                _send_enrollment_email(enrollment)
                messages.success(request, "Berhasil mendaftar ke kursus.")
            return redirect("learning:course_learn", slug=course.slug)

        if "comment_submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                Comment.objects.create(
                    course=course,
                    user=request.user,
                    content=comment_form.cleaned_data["content"],
                )
                messages.success(request, "Komentar berhasil ditambahkan.")
                return redirect(course.get_absolute_url())
        elif "review_submit" in request.POST and enrollment:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                Review.objects.update_or_create(
                    course=course,
                    user=request.user,
                    defaults={
                        "rating": review_form.cleaned_data["rating"],
                        "content": review_form.cleaned_data["content"],
                    },
                )
                messages.success(request, "Review kursus berhasil disimpan.")
                return redirect(course.get_absolute_url())
    else:
        comment_form = CommentForm()
        review_form = ReviewForm()

    comments = course.comments.select_related("user").order_by("-created_at")
    reviews = course.reviews.select_related("user").order_by("-created_at")

    context = {
        "course": course,
        "enrollment": enrollment,
        "comment_form": comment_form,
        "review_form": review_form,
        "comments": comments,
        "reviews": reviews,
        "average_rating": course.average_rating(),
    }
    return render(request, "learning/course_detail.html", context)


@login_required
def course_learn(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment = get_object_or_404(Enrollment, course=course, student=request.user)
    lessons = course.lessons.all()

    if request.method == "POST" and "complete_lesson" in request.POST:
        lesson_id = request.POST.get("lesson_id")
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            messages.success(request, f"Materi '{lesson.title}' ditandai selesai.")

    progress_percentage = enrollment.progress_percentage()
    all_completed = progress_percentage == 100 and lessons.exists()
    if all_completed and not enrollment.is_completed:
        enrollment.is_completed = True
        enrollment.completed_at = timezone.now()
        enrollment.save()

    quizzes = course.quizzes.all()

    context = {
        "course": course,
        "enrollment": enrollment,
        "lessons": lessons,
        "progress_percentage": progress_percentage,
        "quizzes": quizzes,
    }
    return render(request, "learning/course_learn.html", context)


@login_required
def quiz_detail(request: HttpRequest, slug: str, quiz_id: int) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment = get_object_or_404(Enrollment, course=course, student=request.user)
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__choices"), id=quiz_id, course=course
    )

    questions = list(quiz.questions.all())
    if not questions:
        raise Http404("Quiz belum memiliki soal.")

    if request.method == "POST":
        total_questions = len(questions)
        correct_count = 0
        submission = QuizSubmission.objects.create(quiz=quiz, enrollment=enrollment)
        for question in questions:
            choice_id = request.POST.get(f"question_{question.id}")
            if not choice_id:
                continue
            try:
                selected_choice = question.choices.get(id=choice_id)
            except Choice.DoesNotExist:
                continue
            is_correct = selected_choice.is_correct
            if is_correct:
                correct_count += 1
            QuizAnswer.objects.create(
                submission=submission,
                question=question,
                selected_choice=selected_choice,
                is_correct=is_correct,
            )

        score = (correct_count / total_questions) * 100
        submission.score = score
        submission.is_passed = score >= 60
        submission.save()

        messages.info(
            request,
            f"Quiz selesai. Skor Anda: {score:.0f}/100. "
            f"{'Lulus' if submission.is_passed else 'Belum lulus'}.",
        )

        if quiz.is_final and submission.is_passed:
            _issue_certificate_if_needed(enrollment)

        return redirect("learning:course_learn", slug=course.slug)

    context = {
        "course": course,
        "quiz": quiz,
        "questions": questions,
    }
    return render(request, "learning/quiz_detail.html", context)


@login_required
def certificate_view(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment = get_object_or_404(Enrollment, course=course, student=request.user)

    if not enrollment.is_completed:
        messages.error(request, "Anda belum menyelesaikan kursus ini.")
        return redirect("learning:course_learn", slug=course.slug)

    certificate = _issue_certificate_if_needed(enrollment)

    context = {
        "course": course,
        "enrollment": enrollment,
        "certificate": certificate,
    }
    return render(request, "learning/certificate.html", context)


@login_required
def instructor_dashboard(request: HttpRequest) -> HttpResponse:
    user = request.user
    if not user.is_instructor():
        messages.error(request, "Hanya instruktur yang dapat mengakses dashboard instruktur.")
        return redirect("learning:home")

    courses = (
        Course.objects.filter(instructor=user)
        .annotate(num_students=Count("enrollments"))
        .order_by("-created_at")
    )

    context = {
        "courses": courses,
    }
    return render(request, "learning/instructor_dashboard.html", context)


@login_required
def course_create(request: HttpRequest) -> HttpResponse:
    if not request.user.is_instructor():
        messages.error(request, "Hanya instruktur yang dapat membuat kursus.")
        return redirect("learning:home")

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            form.save_m2m()
            messages.success(request, "Kursus berhasil dibuat.")
            return redirect("learning:instructor_dashboard")
    else:
        form = CourseForm()

    return render(request, "learning/course_form.html", {"form": form, "title": "Buat Kursus"})


@login_required
def course_edit(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug)
    if course.instructor != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki izin untuk mengedit kursus ini.")
        return redirect("learning:instructor_dashboard")

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Kursus berhasil diperbarui.")
            return redirect("learning:instructor_dashboard")
    else:
        form = CourseForm(instance=course)

    return render(request, "learning/course_form.html", {"form": form, "title": "Edit Kursus"})


@login_required
def course_delete(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug)
    if course.instructor != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki izin untuk menghapus kursus ini.")
        return redirect("learning:instructor_dashboard")

    if request.method == "POST":
        course.delete()
        messages.success(request, "Kursus berhasil dihapus.")
        return redirect("learning:instructor_dashboard")

    return render(
        request,
        "learning/course_confirm_delete.html",
        {"course": course},
    )


@login_required
def lesson_create(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug)
    if course.instructor != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki izin untuk menambah materi pada kursus ini.")
        return redirect("learning:instructor_dashboard")

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Materi berhasil dibuat.")
            return redirect("learning:course_edit", slug=course.slug)
    else:
        form = LessonForm()

    return render(
        request,
        "learning/lesson_form.html",
        {"form": form, "course": course, "title": "Tambah Materi"},
    )


@login_required
def lesson_edit(request: HttpRequest, slug: str, lesson_id: int) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if course.instructor != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki izin untuk mengedit materi ini.")
        return redirect("learning:instructor_dashboard")

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Materi berhasil diperbarui.")
            return redirect("learning:course_edit", slug=course.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(
        request,
        "learning/lesson_form.html",
        {"form": form, "course": course, "title": "Edit Materi"},
    )


@login_required
def lesson_delete(request: HttpRequest, slug: str, lesson_id: int) -> HttpResponse:
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if course.instructor != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki izin untuk menghapus materi ini.")
        return redirect("learning:instructor_dashboard")

    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Materi berhasil dihapus.")
        return redirect("learning:course_edit", slug=course.slug)

    return render(
        request,
        "learning/lesson_confirm_delete.html",
        {"lesson": lesson, "course": course},
    )


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("learning:home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.role = form.cleaned_data["role"]
            user.save()
            raw_password = form.cleaned_data["password1"]
            authenticated_user = authenticate(
                request, username=user.username, password=raw_password
            )
            if authenticated_user is not None:
                login(request, authenticated_user)
            messages.success(request, "Registrasi berhasil. Selamat datang di platform!")
            return redirect("learning:home")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    enrollments = (
        Enrollment.objects.filter(student=request.user)
        .select_related("course")
        .order_by("-enrolled_at")
    )

    context = {
        "enrollments": enrollments,
    }
    return render(request, "learning/profile.html", context)


def _send_enrollment_email(enrollment: Enrollment) -> None:
    subject = f"Pendaftaran Kursus: {enrollment.course.title}"
    message = (
        f"Halo {enrollment.student.get_full_name() or enrollment.student.username},\n\n"
        f"Anda telah berhasil mendaftar ke kursus '{enrollment.course.title}'.\n"
        f"Silakan mulai belajar di platform.\n\n"
        f"Terima kasih."
    )
    if enrollment.student.email:
        send_mail(
            subject,
            message,
            None,
            [enrollment.student.email],
            fail_silently=True,
        )


def _issue_certificate_if_needed(enrollment: Enrollment) -> Certificate:
    if hasattr(enrollment, "certificate"):
        return enrollment.certificate
    code = uuid.uuid4().hex[:10].upper()
    certificate = Certificate.objects.create(enrollment=enrollment, code=code)
    return certificate