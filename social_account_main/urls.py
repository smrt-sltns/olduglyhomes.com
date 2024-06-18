from django.conf import settings
from django.shortcuts import render
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


def error_page(request):
    return render(request, "404.html")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('facebook.urls'), name='facebook-urls'),
    path('404',error_page,name="error-page"),
    path("reports/", include("automation.urls"), name="reports"),
    path("conversations/", include("conversations.urls"), name="conversations"),
    path("ad_spend/", include("limit.urls"), name="limit"), 
    path("youtube/", include("youtube.urls"), name="limit"), 
    path('social-auth/', include('social_django.urls', namespace="social")),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
