from rest_framework import serializers
from api.models import Member, ReferralRelation, Transaction, Level
from decimal import Decimal


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for Member model"""
    balance = serializers.SerializerMethodField()
    referred_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id',
            'username',
            'user_type',
            'referral_code',
            'referred_by',
            'balance',
            'is_admin',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'referral_code',
            'referred_by',
            'balance',
            'is_admin',
            'created_at'
        ]
    
    def get_balance(self, obj):
        """Return appropriate balance based on user type"""
        if obj.user_type == 'player':
            return float(obj.balance_vcoins)
        else:  # influencer
            return float(obj.balance_rubles)
    
    def get_referred_by(self, obj):
        """Get ID of the user who referred this member"""
        relation = ReferralRelation.objects.filter(referred=obj, level=1).first()
        if relation:
            return relation.referrer.id
        return None


class MemberAdminSerializer(serializers.ModelSerializer):
    """Serializer for Member model with admin fields"""
    balance = serializers.SerializerMethodField()
    referred_by = serializers.SerializerMethodField()
    total_referrals = serializers.SerializerMethodField()
    total_earned = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id',
            'username',
            'user_type',
            'referral_code',
            'referred_by',
            'balance',
            'is_admin',
            'created_at',
            'total_referrals',
            'total_earned'
        ]
        read_only_fields = fields
    
    def get_balance(self, obj):
        """Return appropriate balance based on user type"""
        if obj.user_type == 'player':
            return float(obj.balance_vcoins)
        else:  # influencer
            return float(obj.balance_rubles)
    
    def get_referred_by(self, obj):
        """Get ID of the user who referred this member"""
        relation = ReferralRelation.objects.filter(referred=obj, level=1).first()
        if relation:
            return relation.referrer.id
        return None
    
    def get_total_referrals(self, obj):
        """Count total referrals"""
        return ReferralRelation.objects.filter(referrer=obj).count()
    
    def get_total_earned(self, obj):
        """Calculate total earned from bonuses"""
        bonus_transactions = Transaction.objects.filter(
            member=obj,
            type='bonus',
            status='completed'
        )
        total = sum(t.amount for t in bonus_transactions)
        return float(total)


class MemberRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration"""
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    referral_code = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    user_type = serializers.ChoiceField(
        choices=['player', 'influencer'],
        required=True
    )
    
    def validate_username(self, value):
        """Check if username is unique"""
        if Member.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_referral_code(self, value):
        """Validate referral code if provided"""
        if value and value.strip():
            if not Member.objects.filter(referral_code=value).exists():
                raise serializers.ValidationError("Invalid referral code")
        return value
    
    def create(self, validated_data):
        """Create new member with referral tracking"""
        referral_code = validated_data.pop('referral_code', None)
        password = validated_data.pop('password')
        
        # Create member
        member = Member.objects.create(**validated_data)
        member.set_password(password)
        member.save()
        
        # Handle referral if code provided
        if referral_code and referral_code.strip():
            referrer = Member.objects.filter(referral_code=referral_code).first()
            if referrer:
                ReferralRelation.create_referral_chain(referrer, member)
                
                # Award bonuses to all referrers in chain
                relations = ReferralRelation.objects.filter(referred=member).order_by('level')
                for relation in relations:
                    if relation.level == 1:
                        bonus_amount = relation.referrer.calculate_referral_bonus(member)
                    else:
                        bonus_amount = relation.referrer.calculate_indirect_bonus(relation.level)
                    
                    # Create transaction for bonus
                    currency = 'vcoins' if relation.referrer.user_type == 'player' else 'rubles'
                    transaction = Transaction.objects.create(
                        member=relation.referrer,
                        type='bonus',
                        amount=bonus_amount,
                        currency=currency,
                        status='completed',
                        description=f"Referral bonus from {member.username} (Level {relation.level})",
                        related_member=member
                    )
                    transaction.complete()
                    
                    # Check for level upgrade
                    Level.check_and_update_member_level(relation.referrer)
        
        return member


class MemberLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Validate credentials"""
        username = data.get('username')
        password = data.get('password')
        
        try:
            member = Member.objects.get(username=username)
            if not member.check_password(password):
                raise serializers.ValidationError("Invalid username or password")
            data['member'] = member
        except Member.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password")
        
        return data


class ReferralRelationSerializer(serializers.ModelSerializer):
    """Serializer for ReferralRelation model"""
    username = serializers.CharField(source='referred.username', read_only=True)
    user_type = serializers.CharField(source='referred.user_type', read_only=True)
    total_earned_from = serializers.SerializerMethodField()
    
    class Meta:
        model = ReferralRelation
        fields = [
            'id',
            'username',
            'user_type',
            'level',
            'created_at',
            'total_earned_from'
        ]
        read_only_fields = fields
    
    def get_total_earned_from(self, obj):
        """Calculate total earned from this referral"""
        transactions = Transaction.objects.filter(
            member=obj.referrer,
            type='bonus',
            related_member=obj.referred,
            status='completed'
        )
        total = sum(t.amount for t in transactions)
        return float(total)


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    transaction_type = serializers.CharField(source='type')
    confirmed_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_type',
            'amount',
            'status',
            'description',
            'created_at',
            'confirmed_at'
        ]
        read_only_fields = fields
    
    def get_confirmed_at(self, obj):
        """Return confirmed_at timestamp"""
        if obj.status == 'completed':
            return obj.created_at
        return None


class LevelSerializer(serializers.ModelSerializer):
    """Serializer for Level model"""
    level = serializers.SerializerMethodField()
    points_required = serializers.IntegerField(source='required_referrals')
    benefits = serializers.SerializerMethodField()
    
    class Meta:
        model = Level
        fields = ['level', 'name', 'points_required', 'benefits']
        read_only_fields = fields
    
    def get_level(self, obj):
        """Return level number based on order"""
        levels_order = {'silver': 1, 'gold': 2, 'platinum': 3}
        return levels_order.get(obj.name, 0)
    
    def get_benefits(self, obj):
        """Return list of benefits for this level"""
        multiplier = float(obj.bonus_multiplier)
        bonus_percent = int((multiplier - 1) * 100)
        
        benefits = []
        if bonus_percent > 0:
            benefits.append(f"{bonus_percent}% bonus on referrals")
        if obj.name in ['gold', 'platinum']:
            benefits.append("Access to special tournaments")
        if obj.name == 'platinum':
            benefits.append("VIP support")
            benefits.append("Exclusive rewards")
        
        return benefits


class BonusSerializer(serializers.Serializer):
    """Serializer for bonus transactions"""
    id = serializers.IntegerField(read_only=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    referral_id = serializers.IntegerField()
    referral_username = serializers.CharField()
    referral_level = serializers.IntegerField()
    reason = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Convert Transaction to Bonus format"""
        # Extract level from description
        level = 1
        if 'Level' in instance.description:
            try:
                level = int(instance.description.split('Level ')[1].split(')')[0])
            except:
                level = 1
        
        return {
            'id': instance.id,
            'amount': float(instance.amount),
            'referral_id': instance.related_member.id if instance.related_member else None,
            'referral_username': instance.related_member.username if instance.related_member else 'Unknown',
            'referral_level': level,
            'reason': instance.description,
            'created_at': instance.created_at
        }


class ReferralStatsSerializer(serializers.Serializer):
    """Serializer for referral statistics"""
    total_referrals = serializers.IntegerField()
    direct_referrals = serializers.IntegerField()
    total_earned = serializers.DecimalField(max_digits=15, decimal_places=2)
    level_breakdown = serializers.ListField(
        child=serializers.DictField()
    )


class ReferralTreeNodeSerializer(serializers.Serializer):
    """Serializer for referral tree nodes"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    user_type = serializers.CharField()
    level = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    children = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    def to_representation(self, instance):
        """Recursively serialize referral tree"""
        if isinstance(instance, dict):
            return instance
        
        return {
            'id': instance.referred.id,
            'username': instance.referred.username,
            'user_type': instance.referred.user_type,
            'level': instance.level,
            'created_at': instance.created_at,
            'children': []
        }


class ManualBonusRequestSerializer(serializers.Serializer):
    """Serializer for manual bonus assignment request"""
    user_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01, required=True)
    reason = serializers.CharField(min_length=1, required=True)


class ConfirmTournamentRequestSerializer(serializers.Serializer):
    """Serializer for tournament confirmation request"""
    user_id = serializers.IntegerField(required=True)
    tournament_name = serializers.CharField(required=True)
    reward_amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0, required=True)


class ConfirmDepositRequestSerializer(serializers.Serializer):
    """Serializer for deposit confirmation request"""
    transaction_id = serializers.IntegerField(required=True)


class SystemStatsSerializer(serializers.Serializer):
    """Serializer for system statistics"""
    total_users = serializers.IntegerField()
    total_players = serializers.IntegerField()
    total_influencers = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_deposits = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_bonuses_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_deposits = serializers.IntegerField()
    active_users_last_30_days = serializers.IntegerField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    timestamp = serializers.DateTimeField(read_only=True)
