from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя"""
    id = models.AutoField(primary_key=True)
    email = models.EmailField(
        "Электронная почта",
        blank=False,
        null=False,
        unique=True,
        max_length=254
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["username"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"],
                name="unique_username_email",
            )
        ]

    def __str__(self):
        return self.username
