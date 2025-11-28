from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .serializers import (
    MessageSerializer,
    MemberSerializer,
    MemberRegistrationSerializer,
    MemberLoginSerializer,
    ReferralRelationSerializer,
    ReferralStatsSerializer,
    ReferralTreeNodeSerializer,
    TransactionSerializer,
    BonusSerializer,
    LevelSerializer
)
from .models import Member, ReferralRelation, Transaction, Level
from .authentication import CookieAuthentication
from decimal import Decimal
import uuid


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


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


class ReferralsListView(APIView):
    """
    Get paginated list of user's direct referrals
    """
    authentication_classes = [CookieAuthentication]
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        responses={200: ReferralRelationSerializer(many=True)}
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
        
        # Get direct referrals (level 1)
        referrals = ReferralRelation.objects.filter(
            referrer=request.user,
            level=1
        ).select_related('referred').order_by('-created_at')
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_referrals = paginator.paginate_queryset(referrals, request)
        
        serializer = ReferralRelationSerializer(paginated_referrals, many=True)
        return paginator.get_paginated_response(serializer.data)


class ReferralStatsView(APIView):
    """
    Get referral statistics
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={200: ReferralStatsSerializer}
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
        
        # Count total and direct referrals
        total_referrals = ReferralRelation.objects.filter(referrer=member).count()
        direct_referrals = ReferralRelation.objects.filter(referrer=member, level=1).count()
        
        # Calculate total earned from bonuses
        bonus_transactions = Transaction.objects.filter(
            member=member,
            type='bonus',
            status='completed'
        )
        total_earned = sum(t.amount for t in bonus_transactions)
        
        # Level breakdown
        level_breakdown = []
        for level in range(1, 11):
            level_relations = ReferralRelation.objects.filter(
                referrer=member,
                level=level
            )
            count = level_relations.count()
            
            if count > 0:
                # Calculate earned at this level
                level_earned = Decimal('0')
                for relation in level_relations:
                    level_transactions = Transaction.objects.filter(
                        member=member,
                        type='bonus',
                        status='completed',
                        related_member=relation.referred
                    )
                    level_earned += sum(t.amount for t in level_transactions)
                
                level_breakdown.append({
                    'level': level,
                    'count': count,
                    'earned': float(level_earned)
                })
        
        data = {
            'total_referrals': total_referrals,
            'direct_referrals': direct_referrals,
            'total_earned': float(total_earned),
            'level_breakdown': level_breakdown
        }
        
        serializer = ReferralStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralTreeView(APIView):
    """
    Get hierarchical referral tree up to 10 levels
    """
    authentication_classes = [CookieAuthentication]

    def build_tree(self, referrer, current_level=1, max_depth=10):
        """Recursively build referral tree"""
        if current_level > max_depth:
            return []
        
        direct_referrals = ReferralRelation.objects.filter(
            referrer=referrer,
            level=1
        ).select_related('referred').order_by('-created_at')
        
        tree = []
        for relation in direct_referrals:
            node = {
                'id': relation.referred.id,
                'username': relation.referred.username,
                'user_type': relation.referred.user_type,
                'level': current_level,
                'created_at': relation.created_at,
                'children': self.build_tree(
                    relation.referred,
                    current_level + 1,
                    max_depth
                )
            }
            tree.append(node)
        
        return tree

    @extend_schema(
        responses={200: ReferralTreeNodeSerializer(many=True)}
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
        
        max_depth = int(request.GET.get('max_depth', 10))
        if max_depth < 1:
            max_depth = 1
        if max_depth > 10:
            max_depth = 10
        
        tree = self.build_tree(request.user, max_depth=max_depth)
        
        serializer = ReferralTreeNodeSerializer(tree, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionsListView(APIView):
    """
    Get paginated transaction history
    """
    authentication_classes = [CookieAuthentication]
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        responses={200: TransactionSerializer(many=True)}
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
        
        # Get all transactions for user
        transactions = Transaction.objects.filter(
            member=request.user
        ).order_by('-created_at')
        
        # Filter by transaction type if provided
        transaction_type = request.GET.get('transaction_type')
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_transactions = paginator.paginate_queryset(transactions, request)
        
        serializer = TransactionSerializer(paginated_transactions, many=True)
        return paginator.get_paginated_response(serializer.data)


class DepositView(APIView):
    """
    Create deposit request
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'amount': {'type': 'number'},
                    'payment_method': {'type': 'string'}
                },
                'required': ['amount']
            }
        },
        responses={201: TransactionSerializer}
    )
    def post(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {
                    'error': 'Authentication required',
                    'detail': 'User is not authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'card')
        
        # Validate amount
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
        except (ValueError, TypeError, Exception):
            return Response(
                {
                    'error': 'Validation error',
                    'detail': 'Amount must be greater than 0'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine currency based on user type
        currency = 'vcoins' if request.user.user_type == 'player' else 'rubles'
        
        # Create deposit transaction with pending status
        transaction = Transaction.objects.create(
            member=request.user,
            type='deposit',
            amount=amount,
            currency=currency,
            status='pending',
            description=f"Deposit request via {payment_method}"
        )
        
        serializer = TransactionSerializer(transaction)
        return Response(
            {
                'message': 'Deposit request created successfully',
                'transaction': serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class BonusesListView(APIView):
    """
    Get paginated bonus history
    """
    authentication_classes = [CookieAuthentication]
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        responses={200: BonusSerializer(many=True)}
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
        
        # Get bonus transactions
        bonuses = Transaction.objects.filter(
            member=request.user,
            type='bonus'
        ).select_related('related_member').order_by('-created_at')
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_bonuses = paginator.paginate_queryset(bonuses, request)
        
        serializer = BonusSerializer(paginated_bonuses, many=True)
        return paginator.get_paginated_response(serializer.data)


class CurrentLevelView(APIView):
    """
    Get current level and progress to next level
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'current_level': {'type': 'integer'},
                    'level_name': {'type': 'string'},
                    'current_points': {'type': 'integer'},
                    'points_for_next_level': {'type': 'integer'},
                    'progress_percentage': {'type': 'number'},
                    'benefits': {'type': 'array', 'items': {'type': 'string'}}
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
        
        # Count direct referrals (points)
        current_points = ReferralRelation.objects.filter(
            referrer=member,
            level=1
        ).count()
        
        # Get current level info
        levels_map = {'none': 0, 'silver': 1, 'gold': 2, 'platinum': 3}
        current_level_num = levels_map.get(member.level, 0)
        level_name = member.level.capitalize() if member.level != 'none' else 'None'
        
        # Get benefits for current level
        benefits = []
        if member.level != 'none':
            try:
                level_obj = Level.objects.get(name=member.level)
                multiplier = float(level_obj.bonus_multiplier)
                bonus_percent = int((multiplier - 1) * 100)
                
                if bonus_percent > 0:
                    benefits.append(f"{bonus_percent}% bonus on referrals")
                if member.level in ['gold', 'platinum']:
                    benefits.append("Access to special tournaments")
                if member.level == 'platinum':
                    benefits.append("VIP support")
                    benefits.append("Exclusive rewards")
            except Level.DoesNotExist:
                pass
        
        # Find next level
        all_levels = Level.objects.all().order_by('required_referrals')
        next_level = None
        for lvl in all_levels:
            if lvl.required_referrals > current_points:
                next_level = lvl
                break
        
        if next_level:
            points_for_next_level = next_level.required_referrals
            # Calculate progress from current level to next
            try:
                current_level_obj = Level.objects.get(name=member.level)
                points_from_current = current_points - current_level_obj.required_referrals
                points_needed = points_for_next_level - current_level_obj.required_referrals
                progress_percentage = (points_from_current / points_needed * 100) if points_needed > 0 else 0
            except Level.DoesNotExist:
                progress_percentage = (current_points / points_for_next_level * 100) if points_for_next_level > 0 else 0
        else:
            points_for_next_level = current_points
            progress_percentage = 100
        
        return Response(
            {
                'current_level': current_level_num,
                'level_name': level_name,
                'current_points': current_points,
                'points_for_next_level': points_for_next_level,
                'progress_percentage': round(progress_percentage, 2),
                'benefits': benefits
            },
            status=status.HTTP_200_OK
        )


class LevelsListView(APIView):
    """
    Get all available levels
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={200: LevelSerializer(many=True)}
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
        
        levels = Level.objects.all().order_by('required_referrals')
        serializer = LevelSerializer(levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
