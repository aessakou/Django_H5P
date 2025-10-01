
from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
	
	USER_TYPE_CHOICES = [
		('admin', 'Administrator'),
		('teacher', 'Teacher'),
		('student', 'Student'),
	]

	user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
	profile_image = models.ImageField(upload_to='teacher_images/', null=True, blank=True)
	bio = models.TextField(blank=True)
	phone_number = models.CharField(max_length=15, blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


	def __str__(self):
		return f"{self.username} ({self.get_user_type_display()})"
	@property
	def is_admin(self):
		return self.user_type == 'admin'
	@property
	def is_teacher(self):
		return self.user_type == 'teacher'
	@property
	def is_student(self):
		return self.user_type == 'student'