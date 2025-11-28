from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
import string
import random


class Member(models.Model):
    """Custom user model for the referral system"""
    
    USER_TYPE_CHOICES = [
        ('player', 'Player'),
        ('influencer', 'Influencer'),
    ]
    
    LEVEL_CHOICES = [
        ('none', 'None'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=128)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='player')
    referral_code = models.CharField(max_length=20, unique=True, db_index=True)
    balance_vcoins = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_rubles = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='none')
    is_admin = models.BooleanField(default=False)
    first_tournament_played = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'members'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password_hash)
    
    @staticmethod
    def generate_referral_code():
        """Generate unique referral code"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=8))
            if not Member.objects.filter(referral_code=code).exists():
                return code
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    # DRF compatibility properties and methods
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def has_perm(self, perm, obj=None):
        """Check if user has permission"""
        return self.is_admin
    
    def has_module_perms(self, app_label):
        """Check if user has module permissions"""
        return self.is_admin
    
    def get_referral_chain(self, max_level=10):
        """Get all referrals in the chain up to max_level"""
        chain = []
        current_level = 1
        current_refs = list(ReferralRelation.objects.filter(
            referrer=self, level=current_level
        ).select_related('referred'))
        
        while current_refs and current_level <= max_level:
            chain.extend(current_refs)
            current_level += 1
            if current_level <= max_level:
                current_refs = list(ReferralRelation.objects.filter(
                    referrer=self, level=current_level
                ).select_related('referred'))
        
        return chain
    
    def calculate_referral_bonus(self, direct_referral):
        """Calculate bonus for referring a new member"""
        # Get member's level configuration
        try:
            level_config = Level.objects.get(name=self.level)
            multiplier = level_config.bonus_multiplier
        except Level.DoesNotExist:
            multiplier = 1.0
        
        # Base bonus for direct referral (level 1)
        base_bonus = 1000
        
        if self.user_type == 'player':
            return base_bonus * multiplier
        else:  # influencer
            # Influencers get money instead of V-Coins
            return (base_bonus * multiplier) / 100  # Example conversion rate
    
    def calculate_indirect_bonus(self, level):
        """Calculate bonus for indirect referrals"""
        # Bonus decreases with level
        # Level 2: 150 V-Coins, Level 3: 100, etc.
        base_bonuses = {
            2: 150,
            3: 100,
            4: 75,
            5: 50,
            6: 40,
            7: 30,
            8: 20,
            9: 15,
            10: 10,
        }
        
        try:
            level_config = Level.objects.get(name=self.level)
            multiplier = level_config.bonus_multiplier
        except Level.DoesNotExist:
            multiplier = 1.0
        
        base_bonus = base_bonuses.get(level, 0)
        
        if self.user_type == 'player':
            return base_bonus * multiplier
        else:  # influencer
            return (base_bonus * multiplier) / 100


class ReferralRelation(models.Model):
    """Track referral relationships and levels"""
    
    referrer = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='referrals_made'
    )
    referred = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='referred_by'
    )
    level = models.IntegerField(default=1)  # 1-10, where 1 is direct referral
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_relations'
        unique_together = ['referrer', 'referred']
        ordering = ['level', '-created_at']
        indexes = [
            models.Index(fields=['referrer', 'level']),
            models.Index(fields=['referred']),
        ]
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.referred.username} (Level {self.level})"
    
    @staticmethod
    def create_referral_chain(referrer, new_member):
        """Create referral chain when a new member joins"""
        # Create direct referral (level 1)
        ReferralRelation.objects.create(
            referrer=referrer,
            referred=new_member,
            level=1
        )
        
        # Find all people who referred the referrer and create chain
        upper_chain = ReferralRelation.objects.filter(
            referred=referrer
        ).order_by('level')
        
        for relation in upper_chain:
            new_level = relation.level + 1
            if new_level <= 10:  # Maximum 10 levels
                ReferralRelation.objects.create(
                    referrer=relation.referrer,
                    referred=new_member,
                    level=new_level
                )


class Transaction(models.Model):
    """Track all financial transactions"""
    
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('bonus', 'Bonus'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    CURRENCY_CHOICES = [
        ('vcoins', 'V-Coins'),
        ('rubles', 'Rubles'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    related_member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member', '-created_at']),
            models.Index(fields=['type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.member.username} - {self.type} {self.amount} {self.currency}"
    
    def complete(self):
        """Mark transaction as completed and update member balance"""
        if self.status == 'completed':
            return
        
        self.status = 'completed'
        
        # Update member balance
        if self.currency == 'vcoins':
            if self.type == 'withdrawal':
                self.member.balance_vcoins -= self.amount
            else:
                self.member.balance_vcoins += self.amount
        elif self.currency == 'rubles':
            if self.type == 'withdrawal':
                self.member.balance_rubles -= self.amount
            else:
                self.member.balance_rubles += self.amount
        
        self.member.save()
        self.save()


class Level(models.Model):
    """Define membership levels and their benefits"""
    
    LEVEL_NAMES = [
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    name = models.CharField(max_length=20, choices=LEVEL_NAMES, unique=True)
    required_referrals = models.IntegerField(default=0)
    bonus_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    
    class Meta:
        db_table = 'levels'
        ordering = ['required_referrals']
    
    def __str__(self):
        return f"{self.name} (x{self.bonus_multiplier})"
    
    @staticmethod
    def check_and_update_member_level(member):
        """Check if member qualifies for level upgrade"""
        # Count direct referrals (level 1)
        referral_count = ReferralRelation.objects.filter(
            referrer=member,
            level=1
        ).count()
        
        # Find highest level member qualifies for
        levels = Level.objects.filter(
            required_referrals__lte=referral_count
        ).order_by('-required_referrals')
        
        if levels.exists():
            new_level = levels.first()
            if member.level != new_level.name:
                member.level = new_level.name
                member.save()
                return True
        
        return False
