from django.urls import path
from . import views

app_name = "h5p"

urlpatterns = [
    # Dashboard
    path("", views.dashboard_view, name="dashboard"),

    # Content management
    path("content/", views.content_list_view, name="content_list"),
    path("content/create/", views.content_create_view, name="content_create"),
    path("content/<int:pk>/edit/", views.content_edit_view, name="content_edit"),
    # path("content/<int:pk>/delete/", views.content_delete, name="content_delete"),

    # Upload & Export
    # path("content/upload/", views.upload_h5p, name="upload_h5p"),
    # path("content/<int:pk>/export/", views.export_h5p, name="export_h5p"),

    # Player
    # path("play/<int:pk>/", views.h5p_player, name="h5p_player"),

    # # AJAX Endpoints
    # path("ajax/content/<int:pk>/progress/", views.save_progress, name="save_progress"),
    # path("ajax/content/<int:pk>/score/", views.save_score, name="save_score"),

    # # Admin routes
    # path("libraries/", views.library_list, name="library_list"),
    # path("libraries/add/", views.library_add, name="library_add"),
    # path("branding/", views.branding_settings, name="branding_settings"),


	path("editor/", views.h5p_content_editor, name="h5p_editor"),
	path("editor/<int:pk>/", views.h5p_content_editor, name="h5p_editor_edit"),

]

