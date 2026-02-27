from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin


class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    forget_token = models.CharField(max_length=1000)


class Image_c(models.Model):
    image = models.ImageField(upload_to='image_convert/', null=True)
    vid = models.FileField(upload_to='image_convert/', null=True)
    video = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=50)
