from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .serializers import (
    MessageSerializer,
    MemberSerializer,
    MemberRegistrationSerializer,
    MemberLoginSerializer
)
from .models import Member
from .authentication import CookieAuthentication
import uuid


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """

    @extend_schema(
        responses={200: MessageSerializer}, description="Get a hello world message"
    )
    def get(self, request):
        data = {"message": "Hello!", "timestamp": timezone.now()}
        serializer = MessageSerializer(data)
        return Response(serializer.data)


class RegisterView(APIView):
    """
    User registration endpoint
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=MemberRegistrationSerializer,
        responses={201: MemberSerializer}
    )
    def post(self, request):
        serializer = MemberRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            member = serializer.save()
            
            # Create session and set cookie
            request.session['member_id'] = member.id
            request.session.save()
            
            # Prepare response
            member_serializer = MemberSerializer(member)
            response = Response(
                {
                    'message': 'User registered successfully',
                    'user': member_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
            # Set HttpOnly cookie
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=settings.SESSION_COOKIE_AGE
            )
            
            return response
        
        return Response(
            {
                'error': 'Validation error',
                'detail': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    User login endpoint
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=MemberLoginSerializer,
        responses={200: MemberSerializer}
    )
    def post(self, request):
        serializer = MemberLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            member = serializer.validated_data['member']
            
            # Create session and set cookie
            request.session['member_id'] = member.id
            request.session.save()
            
            # Prepare response
            member_serializer = MemberSerializer(member)
            response = Response(
                {
                    'message': 'Login successful',
                    'user': member_serializer.data
                },
                status=status.HTTP_200_OK
            )
            
            # Set HttpOnly cookie
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=settings.SESSION_COOKIE_AGE
            )
            
            return response
        
        return Response(
            {
                'error': 'Authentication failed',
                'detail': serializer.errors
            },
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    User logout endpoint
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={200: dict}
    )
    def post(self, request):
        # Clear session
        request.session.flush()
        
        # Prepare response
        response = Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
        
        # Delete cookie
        response.delete_cookie('sessionid')
        
        return response


class MeView(APIView):
    """
    Get current authenticated user
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={200: MemberSerializer}
    )
    def get(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {
                    'error': 'Authentication required',
                    'detail': 'User is not authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = MemberSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    Get and update user profile
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={200: MemberSerializer}
    )
    def get(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {
                    'error': 'Authentication required',
                    'detail': 'User is not authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = MemberSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'}
                }
            }
        },
        responses={200: MemberSerializer}
    )
    def patch(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {
                    'error': 'Authentication required',
                    'detail': 'User is not authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        member = request.user
        username = request.data.get('username')
        
        if username:
            # Check if username is already taken
            if Member.objects.filter(username=username).exclude(id=member.id).exists():
                return Response(
                    {
                        'error': 'Validation error',
                        'detail': 'Username already exists'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            member.username = username
            member.save()
        
        serializer = MemberSerializer(member)
        return Response(
            {
                'message': 'Profile updated successfully',
                'user': serializer.data
            },
            status=status.HTTP_200_OK
        )


class ReferralLinkView(APIView):
    """
    Get user's referral link
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'referral_code': {'type': 'string'},
                    'referral_link': {'type': 'string'}
                }
            }
        }
    )
    def get(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {
                    'error': 'Authentication required',
                    'detail': 'User is not authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        member = request.user
        base_url = request.build_absolute_uri('/').rstrip('/')
        referral_link = f"{base_url}/register?ref={member.referral_code}"
        
        return Response(
            {
                'referral_code': member.referral_code,
                'referral_link': referral_link
            },
            status=status.HTTP_200_OK
        )
