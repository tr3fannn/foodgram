from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """Кастомная модель пользователя"""
    USER = "user"
    ADMIN = "admin"

    ROLES_CHOICES = [
        (USER, "user"),
        (ADMIN, "admin"),
    ]
    id = models.AutoField(primary_key=True)
    email = models.EmailField(
        "Электронная почта",
        blank=False,
        null=False,
        unique=True,
        max_length=254
    )
    role = models.CharField(
        max_length=14,
        choices=ROLES_CHOICES,
        default=USER,
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

    @property
    def is_user_admin(self):
        return self.role == User.ADMIN

    @property
    def is_user(self):
        return self.role == User.USER


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
