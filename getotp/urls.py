from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sign_up, name='sign_up')
]
