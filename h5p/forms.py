from django import forms
from .models import H5PContent, H5PLibrary, BrandingSettings


# 1. Content creation & editing
class H5PContentForm(forms.ModelForm):
    class Meta:
        model = H5PContent
        fields = ["title", "library", "json_content"]


# 2. Upload .h5p package
class H5PUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload H5P File",
        help_text="Upload a .h5p file package",
    )


# 3. Manage H5P libraries
class H5PLibraryForm(forms.ModelForm):
    class Meta:
        model = H5PLibrary
        fields = ["name", "version_major", "version_minor", "version_patch", "runnable"]


# 4. Branding & customization
class BrandingForm(forms.ModelForm):
    class Meta:
        model = BrandingSettings
        fields = ["site_name", "logo", "primary_color", "secondary_color"]
