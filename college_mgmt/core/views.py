
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import Course, Department, Register, LeaveType, LeaveMaster
from .serializers import (
    CourseSerializer,
    DepartmentSerializer,
    RegisterSerializer,
    LeaveTypeSerializer,
    LeaveMasterSerializer,
)

# Configure logging
logger = logging.getLogger(__name__)

# -------------------------------
# Model ViewSets
# -------------------------------

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing departments.

    Provides CRUD operations for department records.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing courses.

    Provides CRUD operations for course records.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class RegisterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user registrations.

    Provides CRUD operations for user registration records.
    """
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing leave types.

    Provides CRUD operations for leave type records.
    """
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer


class LeaveMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing leave applications.

    Provides CRUD operations for leave application records.
    """
    queryset = LeaveMaster.objects.all()
    serializer_class = LeaveMasterSerializer


class usernotfoundAdd(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print("==== Received POST Data ====")
            print(data)

            google_id = data.get('uid')
            username = data.get('user')
            useremail = data.get('email')
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            provider = "google"

            if not google_id or not useremail:
                return JsonResponse({'error': 'Missing google_id or useremail'}, status=400)

            print(f"UID: {google_id}, user: {username}, Email: {useremail}, First: {firstname}, Last: {lastname}")

            
            if not gvpfactinfo.objects.filter(fact_email=useremail).exists():
                gvpfactinfo.objects.create(
                    fact_email=useremail,
                    google_uid=google_id,
                    fact_name=f"{firstname} {lastname}",
                    fact_photo='/static/uploads/profile.png',
                    fact_mobile=0,
                    fact_status=0,
                    isadmin=0,
                    isverified=0
                )

           
            return JsonResponse({'message': 'saved successfully'}, status=200)

        except Exception as e:
            print("==== Error ====")
            print(str(e))
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        return JsonResponse({
            'error': 'Method not allowed. Use POST to update appointment status.'
        }, status=405)

class HelloWorldAPIView(APIView):

    def post(self, request, *args, **kwargs):
       
        return Response({"message": "Hello, World!"}, status=status.HTTP_200_OK)

class GoogleLoginAPIView(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "Google Login API. Please send a POST request with a 'token'."},
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        print("api call")
        try:
            token = request.data.get("token")
            if not token:
                logger.warning("Google login attempt without token")
                return Response(
                    {"status": "error", "message": "Token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(token, str) or len(token.strip()) == 0:
                logger.warning("Invalid token format received")
                return Response(
                    {"status": "error", "message": "Invalid token format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)
            if not CLIENT_ID:
                logger.error("GOOGLE_CLIENT_ID not configured in settings")
                return Response(
                    {"status": "error", "message": "Server configuration error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

           
            try:
                logger.info("Verifying Google ID token")
                idinfo = id_token.verify_oauth2_token(
                    token.strip(),
                    google_requests.Request(),
                    CLIENT_ID
                )
            except ValueError as ve:
                logger.warning(f"Invalid Google token: {ve}")
                return Response(
                    {"status": "error", "message": "Invalid authentication token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except Exception as e:
                logger.error(f"Google token verification error: {e}")
                return Response(
                    {"status": "error", "message": "Authentication service error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

   
            email = idinfo.get("email")
            name = idinfo.get("name", "").strip()
            sub = idinfo.get("sub")

            if not email:
                logger.warning("No email returned from Google token")
                return Response(
                    {"status": "error", "message": "Email not provided by authentication service"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            allowed_domain = "@gujaratvidyapith.org"
            if not email.endswith(allowed_domain):
                logger.warning(f"Access denied for email domain: {email}")
                return Response(
                    {"status": "error", "message": f"Access restricted to {allowed_domain} domain"},
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                logger.info(f"Processing user: {email}")
                user, created = Register.objects.get_or_create(
                    email=email,
                    defaults={
                        "name": name,
                        "reg_type": Register.STUDENT,
                        "guid": sub
                    }
                )

                updated = False
                if name and user.name != name:
                    user.name = name
                    updated = True
                    logger.info(f"Updated name for user {email}")

                if not user.guid and sub:
                    user.guid = sub
                    updated = True
                    logger.info(f"Updated GUID for user {email}")

                if updated:
                    user.save()
                    logger.info(f"Saved updated information for user {email}")

                logger.info(f"Successfully processed user {email}, created: {created}")

            except Exception as db_err:
                logger.error(f"Database error for user {email}: {db_err}")
                return Response(
                    {"status": "error", "message": "Database operation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "status": "success",
                "email": user.email,
                "name": user.name,
                "user_id": user.id,
                "new_user": created,
                "reg_type": user.reg_type
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error in Google login: {e}")
            return Response(
                {"status": "error", "message": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
