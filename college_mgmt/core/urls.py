# core/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r"departments", DepartmentViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"register1", RegisterViewSet)
router.register(r"leave_types", LeaveTypeViewSet)
router.register(r"leave_master", LeaveMasterViewSet)

urlpatterns = [
    path("api/auth/google/", GoogleLoginAPIView.as_view(), name="google_login"),
    path("", include(router.urls)),
]
