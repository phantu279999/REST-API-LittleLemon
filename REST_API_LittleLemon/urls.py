from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path("api/", include("Api.urls")),
	path('admin/', admin.site.urls),

	path('auth/', include('djoser.urls')),
	path('auth/', include('djoser.urls.authtoken')),
]
