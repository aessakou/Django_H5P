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

    # Export / JSON endpoint used by player
    path("content/<int:pk>/json/", views.content_export_view, name="content_json"),

    # Player
    path("play/<int:pk>/", views.player_view, name="h5p_player"),

	path("editor/", views.h5p_content_editor, name="h5p_editor"),
	path("editor/<int:pk>/", views.h5p_content_editor, name="h5p_editor_edit"),

    # Upload .h5p
    path("upload/", views.upload_h5p_view, name="upload"),

    # Serve extracted content files (e.g., h5p.json and assets)
    path("content/<int:pk>/files/<path:path>", views.content_file_view, name="content_file"),
]
