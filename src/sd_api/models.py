import uuid
from django.db import models
from django.core import serializers


from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, username, age=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Entrer un nom d'utilisateur")
        if age is None and not extra_fields.get('is_superuser', True):
            raise ValueError("L'âge est obligatoire")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('age', None)
        superuser = self.create_user(username, password, **extra_fields)
        return superuser

    # def modify_user(self, username, password=None):
    #     # pour conformité RGPD
    #     pass

    # def delete_user(self, username, password=None, delete_confirmation=False):
    #     # autoriser la suppression pour conformité RGPD
    #     pass


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, blank=False)
    # email = models.EmailField(max_length=150, unique=True, blank=False)
    age = models.PositiveIntegerField(validators=[MinValueValidator(15), MaxValueValidator(120)],
                                      blank=False, null=True)
    can_be_contacted = models.BooleanField(blank=False, default=False)
    can_data_be_shared = models.BooleanField(blank=False, default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # last_login
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Choices:
    # Project type
    BACK_END = 'BAE'
    FRONT_END = 'FRE'
    IOS = 'IOS'
    ANDROID = 'AND'
    PROJECT_TYPE_CHOICES = [
        (BACK_END, 'Back-End'),
        (FRONT_END, 'Front-End'),
        (IOS, 'IOS'),
        (ANDROID, 'Android'),
    ]

    # Issue priority
    LOW = 'LOW'
    MEDIUM = 'MED'
    HIGH = 'HIGH'
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    # Issue tag
    BUG = 'BUG'
    FEATURE = 'FEAT'
    TASK = 'TASK'
    TAG_CHOICES = [
        (BUG, 'Bug'),
        (FEATURE, 'Feature'),
        (TASK, 'Task'),
    ]

    # Issue status
    TODO = 'TODO'
    IN_PROGRESS = 'INPR'
    FINISHED = 'FINI'
    STATUS_CHOICES = [
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (FINISHED, 'Finished'),
    ]


class TimestampModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AuthorModel(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='%(class)ss')

    class Meta:
        abstract = True


class Project(TimestampModel, AuthorModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=3, choices=Choices.PROJECT_TYPE_CHOICES)


class Contributor(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contributions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')


class Issue(TimestampModel, AuthorModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_issues')
    priority = models.CharField(max_length=4, choices=Choices.PRIORITY_CHOICES, blank=False)
    tag = models.CharField(max_length=4, choices=Choices.TAG_CHOICES, blank=False)
    status = models.CharField(max_length=4, choices=Choices.STATUS_CHOICES, default=Choices.TODO)


class Comment(TimestampModel, AuthorModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
