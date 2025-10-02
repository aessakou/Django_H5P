from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.utils.encoding import smart_str
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import H5PContent, H5PResult, H5PLibrary
from .forms import H5PContentForm, H5PUploadForm
from .utils import (
    extract_h5p_archive,
    load_h5p_json,
    derive_library_from_h5p_json,
    get_content_storage_dir,
    safe_path_join,
)
import os

@login_required
def h5p_content_editor(request, pk=None):
    """
    Renders H5P editor for creating or editing content.
    """
    if pk:
        content = get_object_or_404(H5PContent, pk=pk)
    else:
        content = None

    if request.method == "POST":
        form = H5PContentForm(request.POST, instance=content)
        if form.is_valid():
            new_content = form.save(commit=False)
            new_content.created_by = request.user
            new_content.save()
            # After saving, redirect to player or content list
            return redirect("h5p:h5p_player", pk=new_content.pk)
    else:
        form = H5PContentForm(instance=content)

    return render(request, "h5p/h5p_editor.html", {"form": form, "content": content})


User = get_user_model()


# ---------------------------
# Admin Dashboard
# ---------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Show system-wide stats and management tools."""
    total_users = User.objects.count()
    total_content = H5PContent.objects.count()
    total_results = H5PResult.objects.count()
    recent_content = H5PContent.objects.order_by("-created_at")[:5]
    libraries = H5PLibrary.objects.all()

    context = {
        "total_users": total_users,
        "total_content": total_content,
        "total_results": total_results,
        "recent_content": recent_content,
        "libraries": libraries,
    }
    return render(request, "h5p/admin_dashboard.html", context)


# ---------------------------
# Teacher Dashboard
# ---------------------------
def is_teacher(user):
    # Example: define teachers as non-admins who can create content
    return not user.is_staff and user.has_perm("h5p.add_h5pcontent")

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Show teacher-specific stats and tools."""
    user_content = H5PContent.objects.filter(created_by=request.user)
    content_count = user_content.count()
    recent_content = user_content.order_by("-created_at")[:5]

    user_results = H5PResult.objects.filter(user=request.user)
    completed_count = user_results.filter(completed=True).count()

    context = {
        "user_content": user_content,
        "content_count": content_count,
        "recent_content": recent_content,
        "completed_count": completed_count,
    }
    return render(request, "h5p/teacher_dashboard.html", context)


# ---------------------------
# 1. Dashboard View
# ---------------------------
@login_required
def dashboard_view(request):
    """Display stats, recent content, and quick actions."""
    recent_content = H5PContent.objects.order_by("-created_at")[:5]
    total_content = H5PContent.objects.count()
    total_results = H5PResult.objects.count()

    context = {
        "recent_content": recent_content,
        "total_content": total_content,
        "total_results": total_results,
    }
    return render(request, "h5p/dashboard.html", context)


# ---------------------------
# 2. Content Management Views
# ---------------------------

@login_required
def content_list_view(request):
    """Show a searchable and filterable list of H5P content."""
    query = request.GET.get("q", "")
    if query:
        contents = H5PContent.objects.filter(title__icontains=query)
    else:
        contents = H5PContent.objects.all()

    return render(request, "h5p/content_list.html", {"contents": contents, "query": query})


@login_required
def content_create_view(request):
    """Create new H5P content."""
    if request.method == "POST":
        form = H5PContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.created_by = request.user
            content.save()
            return redirect("h5p:content_list")
    else:
        form = H5PContentForm()
    return render(request, "h5p/content_form.html", {"form": form})


@login_required
def content_edit_view(request, pk):
    """Edit existing H5P content."""
    content = get_object_or_404(H5PContent, pk=pk)
    if request.method == "POST":
        form = H5PContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect("h5p:content_list")
    else:
        form = H5PContentForm(instance=content)
    return render(request, "h5p/content_form.html", {"form": form})


@login_required
def content_export_view(request, pk):
    """Export H5P content as JSON (placeholder for real .h5p export)."""
    content = get_object_or_404(H5PContent, pk=pk)
    return JsonResponse(content.json_content)


# ---------------------------
# 3. Player View
# ---------------------------

@login_required
def player_view(request, pk):
    """Render H5P content and track progress."""
    content = get_object_or_404(H5PContent, pk=pk)

    if request.method == "POST":
        # Example: store results
        score = int(request.POST.get("score", 0))
        max_score = int(request.POST.get("max_score", 0))
        H5PResult.objects.update_or_create(
            user=request.user,
            content=content,
            defaults={"score": score, "max_score": max_score, "completed": True},
        )
        return JsonResponse({"status": "success", "score": score})

    return render(request, "h5p/player.html", {"content": content})


# ---------------------------
# 4. Upload .h5p Package
# ---------------------------

@login_required
@require_http_methods(["GET", "POST"])
def upload_h5p_view(request):
    """Upload a .h5p file, extract, store metadata, and create H5PContent."""
    if request.method == "POST":
        form = H5PUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            file_bytes = uploaded_file.read()

            # Ensure a placeholder library exists to satisfy FK constraint
            placeholder_library, _ = H5PLibrary.objects.get_or_create(
                name="Temporary",
                version_major=0,
                version_minor=0,
                version_patch=0,
                defaults={"runnable": False},
            )

            # Create a temporary content to get an ID for storage
            temp_content = H5PContent.objects.create(
                title=uploaded_file.name,
                library=placeholder_library,
                json_content={},
                created_by=request.user,
            )

            content_dir = get_content_storage_dir(temp_content.id)
            extract_h5p_archive(file_bytes, content_dir)
            h5p_json = load_h5p_json(content_dir)
            name, maj, mino, pat = derive_library_from_h5p_json(h5p_json)

            # Ensure library exists/created
            library, _ = H5PLibrary.objects.get_or_create(
                name=name,
                version_major=maj,
                version_minor=mino,
                version_patch=pat,
                defaults={"runnable": True},
            )

            temp_content.title = h5p_json.get("title") or temp_content.title
            temp_content.library = library
            temp_content.json_content = h5p_json
            temp_content.save()

            return redirect("h5p:h5p_player", pk=temp_content.pk)
    else:
        form = H5PUploadForm()

    return render(request, "h5p/upload.html", {"form": form})


# ---------------------------
# 5. Serve Extracted Content Files
# ---------------------------

@login_required
def content_file_view(request, pk, path):
    """Serve files from extracted H5P content directory securely."""
    content = get_object_or_404(H5PContent, pk=pk)
    root_dir = get_content_storage_dir(content.id)
    try:
        full_path = safe_path_join(root_dir, path)
    except ValueError:
        raise Http404
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise Http404
    return FileResponse(open(full_path, "rb"))
