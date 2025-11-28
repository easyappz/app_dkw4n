from django.contrib import admin
from .models import Member, ReferralRelation, Transaction, Level


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'user_type',
        'referral_code',
        'balance_vcoins',
        'balance_rubles',
        'level',
        'is_admin',
        'first_tournament_played',
        'created_at'
    )
    list_filter = ('user_type', 'level', 'is_admin', 'first_tournament_played', 'created_at')
    search_fields = ('username', 'referral_code')
    readonly_fields = ('referral_code', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'password_hash', 'user_type', 'referral_code')
        }),
        ('Balances', {
            'fields': ('balance_vcoins', 'balance_rubles')
        }),
        ('Status', {
            'fields': ('level', 'is_admin', 'first_tournament_played')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ReferralRelation)
class ReferralRelationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'referrer',
        'referred',
        'level',
        'created_at'
    )
    list_filter = ('level', 'created_at')
    search_fields = ('referrer__username', 'referred__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('referrer', 'referred', 'level')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'member',
        'type',
        'amount',
        'currency',
        'status',
        'related_member',
        'created_at'
    )
    list_filter = ('type', 'currency', 'status', 'created_at')
    search_fields = ('member__username', 'related_member__username', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('member', 'type', 'amount', 'currency', 'status')
        }),
        ('Details', {
            'fields': ('description', 'related_member')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'required_referrals',
        'bonus_multiplier'
    )
    list_filter = ('name',)
    ordering = ('required_referrals',)
    
    fieldsets = (
        ('Level Information', {
            'fields': ('name', 'required_referrals', 'bonus_multiplier')
        }),
    )
