from django.db import models
from django.conf import settings  # ✅ use dynamic user model

# 1. H5P Library (content type definition)
class H5PLibrary(models.Model):
    name = models.CharField(max_length=200)
    version_major = models.IntegerField()
    version_minor = models.IntegerField()
    version_patch = models.IntegerField()
    runnable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.version_major}.{self.version_minor}.{self.version_patch}"


# 2. H5P Content (an instance of a library)
class H5PContent(models.Model):
    title = models.CharField(max_length=255)
    library = models.ForeignKey(H5PLibrary, on_delete=models.CASCADE, related_name="contents")
    json_content = models.JSONField()  # stores H5P JSON config
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 3. H5P Result (tracks user score/progress)
class H5PResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(H5PContent, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content")  # one result per user per content


# 4. H5P Content User Data (custom user data like notes, progress)
class H5PContentUserData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(H5PContent, on_delete=models.CASCADE)
    data = models.JSONField()  # stores user-specific JSON data

    class Meta:
        unique_together = ("user", "content")


# 5. H5P Content Share (sharing content between users)
class H5PContentShare(models.Model):
    content = models.ForeignKey(H5PContent, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shared_contents")
    can_edit = models.BooleanField(default=False)


# 6. Branding Settings (platform-level customization)
class BrandingSettings(models.Model):
    site_name = models.CharField(max_length=255, default="My H5P Platform")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#000000")  # hex color
    secondary_color = models.CharField(max_length=7, default="#FFFFFF")
    updated_at = models.DateTimeField(auto_now=True)
