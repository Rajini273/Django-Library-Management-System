from django.db import models
from django.contrib.auth.models import User


# =========================
# BOOK MODEL
# =========================

class Book(models.Model):

    title = models.CharField(
        max_length=200
    )

    author = models.CharField(
        max_length=100
    )

    category = models.CharField(
        max_length=100
    )

    isbn = models.CharField(
        max_length=20,
        unique=True
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    available_quantity = models.PositiveIntegerField(
        default=1
    )

    published_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


# =========================
# MEMBER MODEL
# =========================

class Member(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    membership_id = models.CharField(
        max_length=20,
        unique=True
    )

    joined_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# =========================
# ISSUE MODEL
# =========================

class Issue(models.Model):

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE
    )

    issue_date = models.DateField(
        auto_now_add=True
    )

    due_date = models.DateField()

    return_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default='Issued'
    )

    fine = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.book.title} - {self.member.name}"