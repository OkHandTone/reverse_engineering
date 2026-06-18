from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuthUserManager(UserManager):
    """Manager compatible avec create_user / create_superuser de Django."""

    def _prepare_required_fields(self, extra_fields):
        required = ('phone', 'first_name', 'last_name', 'identification_number')
        missing = [field for field in required if not extra_fields.get(field)]
        if missing:
            raise ValueError(
                'The following fields must be set: {}'.format(', '.join(missing))
            )

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        self._prepare_required_fields(extra_fields)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'SUPERADMIN')
        self._prepare_required_fields(extra_fields)
        return super().create_superuser(username, email, password, **extra_fields)


class AuthUser(AbstractUser):
    class UserType(models.TextChoices):
        CLIENT = 'CLIENT', _('Client')
        WORKER = 'WORKER', _('Worker')
        SUPERADMIN = 'SUPERADMIN', _('Superadmin')

    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    identification_number = models.CharField(max_length=20, unique=True, db_index=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
    )
    client = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'user_type': UserType.CLIENT},
        related_name='workers',
    )
    business = models.ForeignKey(
        'business_management.Business',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workers',
    )

    objects = AuthUserManager()

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
        'phone',
        'identification_number',
    ]

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return (
            f'{self.username} - {self.first_name} {self.last_name} '
            f'({self.get_user_type_display()})'
        )
