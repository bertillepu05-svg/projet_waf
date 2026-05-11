from django.contrib import admin
from django.urls import path, include
from waf_app import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', blog_views.blog, name='home'),           # Page d'accueil (blog)
    path('blog/', blog_views.blog, name='blog'),
    path('blog/search/', blog_views.blog_search, name='blog_search'),
    path('blog/comment/', blog_views.blog_comment, name='blog_comment'),
    path('waf/', include('waf_app.urls')),            # Pages WAF
]