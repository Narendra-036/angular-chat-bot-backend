from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager





class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # This will hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser):
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True, primary_key=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  # Login with email
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # This hashes the password before saving it

    def check_password(self, raw_password):
        
        if self.password == raw_password:
            return True
        else:
            return False
        
        
    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']




class Room(models.Model):
    name = models.CharField(max_length=100)
    user = models.ManyToManyField(User, related_name='user_rooms')
    date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    slug = models.SlugField(max_length=100, unique=True)
    
    def __str__(self):
        # Return a string representation of the room by listing all usernames
        users = self.user.all()  # Fetch all users in this room
        user_names = ', '.join([user.username for user in users])
        return f"Room: {self.name}, Users: {user_names}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'room'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['name']



class Messeges(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.message
    
        

