from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from datetime import timedelta
from .serializers import (
    MessageSerializer,
    MemberSerializer,
    MemberAdminSerializer,
    MemberRegistrationSerializer,
    MemberLoginSerializer,
    ReferralRelationSerializer,
    ReferralStatsSerializer,
    ReferralTreeNodeSerializer,
    TransactionSerializer,
    BonusSerializer,
    LevelSerializer,
    ManualBonusRequestSerializer,
    ConfirmTournamentRequestSerializer,
    ConfirmDepositRequestSerializer,
    SystemStatsSerializer
)
from .models import Member, ReferralRelation, Transaction, Level
from .authentication import CookieAuthentication
from decimal import Decimal
import uuid


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


def check_admin_permission(request):
    """Check if user is authenticated and is admin"""
    if not request.user or request.user.is_anonymous:
        return False, Response(
            {
                'error': 'Authentication required',
                'detail': 'User is not authenticated'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not request.user.is_admin:
        return False, Response(
            {
                'error': 'Permission denied',
                'detail': 'Admin access required'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    return True, None


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
            status='confirmed'
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
                        status='confirmed',
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
                'required': ['amount', 'payment_method']
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
            points_for_next_level = None
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


# Admin Views

class AdminUsersListView(APIView):
    """
    Get all users (Admin only)
    """
    authentication_classes = [CookieAuthentication]
    pagination_class = AdminResultsSetPagination

    @extend_schema(
        responses={200: MemberAdminSerializer(many=True)}
    )
    def get(self, request):
        is_admin, error_response = check_admin_permission(request)
        if not is_admin:
            return error_response
        
        # Get all members
        members = Member.objects.all().order_by('-created_at')
        
        # Filter by user_type if provided
        user_type = request.GET.get('user_type')
        if user_type and user_type in ['player', 'influencer']:
            members = members.filter(user_type=user_type)
        
        # Search by username if provided
        search = request.GET.get('search')
        if search:
            members = members.filter(username__icontains=search)
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_members = paginator.paginate_queryset(members, request)
        
        serializer = MemberAdminSerializer(paginated_members, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminBonusView(APIView):
    """
    Manual bonus assignment (Admin only)
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        request=ManualBonusRequestSerializer,
        responses={201: BonusSerializer}
    )
    def post(self, request):
        is_admin, error_response = check_admin_permission(request)
        if not is_admin:
            return error_response
        
        serializer = ManualBonusRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Validation error',
                    'detail': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data['user_id']
        amount = serializer.validated_data['amount']
        reason = serializer.validated_data['reason']
        
        # Get user
        try:
            member = Member.objects.get(id=user_id)
        except Member.DoesNotExist:
            return Response(
                {
                    'error': 'Not found',
                    'detail': f'User with id {user_id} not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine currency based on user type
        currency = 'vcoins' if member.user_type == 'player' else 'rubles'
        
        # Create bonus transaction
        transaction = Transaction.objects.create(
            member=member,
            type='bonus',
            amount=amount,
            currency=currency,
            status='confirmed',
            description=f"Manual bonus: {reason}"
        )
        transaction.complete()
        
        bonus_serializer = BonusSerializer(transaction)
        return Response(
            {
                'message': 'Bonus assigned successfully',
                'bonus': bonus_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class ConfirmTournamentView(APIView):
    """
    Confirm tournament participation (Admin only)
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        request=ConfirmTournamentRequestSerializer,
        responses={201: TransactionSerializer}
    )
    def post(self, request):
        is_admin, error_response = check_admin_permission(request)
        if not is_admin:
            return error_response
        
        serializer = ConfirmTournamentRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Validation error',
                    'detail': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data['user_id']
        tournament_name = serializer.validated_data['tournament_name']
        reward_amount = serializer.validated_data['reward_amount']
        
        # Get user
        try:
            member = Member.objects.get(id=user_id)
        except Member.DoesNotExist:
            return Response(
                {
                    'error': 'Not found',
                    'detail': f'User with id {user_id} not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine currency based on user type
        currency = 'vcoins' if member.user_type == 'player' else 'rubles'
        
        # Create tournament transaction
        transaction = Transaction.objects.create(
            member=member,
            type='tournament',
            amount=reward_amount,
            currency=currency,
            status='confirmed',
            description=f"Tournament reward: {tournament_name}"
        )
        transaction.complete()
        
        # If this is the first tournament, trigger referral bonuses
        if not member.first_tournament_played:
            member.first_tournament_played = True
            member.save()
            
            # Award bonuses to referral chain (up to 10 levels)
            relations = ReferralRelation.objects.filter(
                referred=member
            ).select_related('referrer').order_by('level')
            
            for relation in relations:
                if relation.level == 1:
                    bonus_amount = relation.referrer.calculate_referral_bonus(member)
                else:
                    bonus_amount = relation.referrer.calculate_indirect_bonus(relation.level)
                
                # Create transaction for bonus
                referrer_currency = 'vcoins' if relation.referrer.user_type == 'player' else 'rubles'
                bonus_transaction = Transaction.objects.create(
                    member=relation.referrer,
                    type='bonus',
                    amount=bonus_amount,
                    currency=referrer_currency,
                    status='confirmed',
                    description=f"First tournament bonus from {member.username} (Level {relation.level})",
                    related_member=member
                )
                bonus_transaction.complete()
        
        transaction_serializer = TransactionSerializer(transaction)
        return Response(
            {
                'message': 'Tournament confirmed successfully',
                'transaction': transaction_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class ConfirmDepositView(APIView):
    """
    Confirm deposit (Admin only)
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        request=ConfirmDepositRequestSerializer,
        responses={200: TransactionSerializer}
    )
    def post(self, request):
        is_admin, error_response = check_admin_permission(request)
        if not is_admin:
            return error_response
        
        serializer = ConfirmDepositRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Validation error',
                    'detail': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction_id = serializer.validated_data['transaction_id']
        
        # Get transaction
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response(
                {
                    'error': 'Not found',
                    'detail': f'Transaction with id {transaction_id} not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if transaction is a deposit and is pending
        if transaction.type != 'deposit':
            return Response(
                {
                    'error': 'Invalid operation',
                    'detail': 'Transaction is not a deposit'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if transaction.status == 'confirmed':
            return Response(
                {
                    'error': 'Invalid operation',
                    'detail': 'Deposit already confirmed'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Complete the deposit transaction
        transaction.complete()
        
        # If user is an influencer, award 10% to their referrer
        member = transaction.member
        direct_referrer_relation = ReferralRelation.objects.filter(
            referred=member,
            level=1
        ).select_related('referrer').first()
        
        if direct_referrer_relation and direct_referrer_relation.referrer.user_type == 'influencer':
            # Award 10% of deposit to direct referrer
            bonus_amount = transaction.amount * Decimal('0.10')
            
            bonus_transaction = Transaction.objects.create(
                member=direct_referrer_relation.referrer,
                type='bonus',
                amount=bonus_amount,
                currency='rubles',
                status='confirmed',
                description=f"10% deposit bonus from {member.username}",
                related_member=member
            )
            bonus_transaction.complete()
        
        transaction_serializer = TransactionSerializer(transaction)
        return Response(
            {
                'message': 'Deposit confirmed successfully',
                'transaction': transaction_serializer.data
            },
            status=status.HTTP_200_OK
        )


class AdminStatsView(APIView):
    """
    Get system statistics (Admin only)
    """
    authentication_classes = [CookieAuthentication]

    @extend_schema(
        responses={200: SystemStatsSerializer}
    )
    def get(self, request):
        is_admin, error_response = check_admin_permission(request)
        if not is_admin:
            return error_response
        
        # Count users
        total_users = Member.objects.count()
        total_players = Member.objects.filter(user_type='player').count()
        total_influencers = Member.objects.filter(user_type='influencer').count()
        
        # Count transactions
        total_transactions = Transaction.objects.count()
        
        # Calculate total deposits
        deposit_transactions = Transaction.objects.filter(
            type='deposit',
            status='confirmed'
        )
        total_deposits = sum(t.amount for t in deposit_transactions)
        
        # Calculate total bonuses paid
        bonus_transactions = Transaction.objects.filter(
            type='bonus',
            status='confirmed'
        )
        total_bonuses_paid = sum(t.amount for t in bonus_transactions)
        
        # Count pending deposits
        pending_deposits = Transaction.objects.filter(
            type='deposit',
            status='pending'
        ).count()
        
        # Count active users in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users_last_30_days = Member.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        data = {
            'total_users': total_users,
            'total_players': total_players,
            'total_influencers': total_influencers,
            'total_transactions': total_transactions,
            'total_deposits': float(total_deposits),
            'total_bonuses_paid': float(total_bonuses_paid),
            'pending_deposits': pending_deposits,
            'active_users_last_30_days': active_users_last_30_days
        }
        
        serializer = SystemStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
