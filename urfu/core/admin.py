from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    Student,
    Teacher,
    Subject,
    Group,
    RefreshToken,
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "department")
    search_fields = ("full_name", "email", "department")
    list_filter = ("department",)
    ordering = ("full_name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher")
    search_fields = ("title", "teacher__full_name")
    list_filter = ("teacher",)
    ordering = ("title",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "subject")
    search_fields = ("name", "subject__title")
    list_filter = ("subject",)
    ordering = ("name",)


class StudentAdmin(BaseUserAdmin):
    model = Student

    list_display = (
        "username",
        "full_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "full_name", "email")
    ordering = ("username",)
    filter_horizontal = ("groups",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("full_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "full_name",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(Student, StudentAdmin)


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created_at",
        "expires_at",
        "used_at",
        "ip_address",
    )
    list_filter = ("used_at", "expires_at", "created_at")
    search_fields = ("user__username", "ip_address", "user_agent")
    readonly_fields = (
        "id",
        "user",
        "token_hash",
        "created_at",
        "expires_at",
        "used_at",
        "user_agent",
        "ip_address",
    )
    ordering = ("-created_at",)
