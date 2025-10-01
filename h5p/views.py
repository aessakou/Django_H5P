from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import H5PContent, H5PResult
from .forms import H5PContentForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import H5PContent, H5PResult, H5PLibrary
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import H5PContentForm
from .models import H5PContent

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
