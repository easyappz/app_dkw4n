from django.core.management.base import BaseCommand
from django.core.management import call_command
from api.models import Member, ReferralRelation, Transaction
from decimal import Decimal
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create test users in referral chain from Tim and fund their balances'

    def handle(self, *args, **options):
        self.stdout.write('Starting test user generation...')
        
        # Find Tim
        try:
            tim = Member.objects.get(username='Tim')
            self.stdout.write(self.style.SUCCESS(f'Found user Tim (referral code: {tim.referral_code})'))
        except Member.DoesNotExist:
            self.stdout.write(self.style.ERROR('User Tim not found. Please create Tim first.'))
            return
        
        # Create 4 users in referral chain
        users_data = [
            {'username': 'TimRef1', 'password': 'Password123!', 'referrer': tim},
            {'username': 'TimRef2', 'password': 'Password123!', 'referrer': None},
            {'username': 'TimRef3', 'password': 'Password123!', 'referrer': None},
            {'username': 'TimRef4', 'password': 'Password123!', 'referrer': None},
        ]
        
        created_users = []
        
        for i, user_data in enumerate(users_data):
            # Check if user already exists
            if Member.objects.filter(username=user_data['username']).exists():
                self.stdout.write(self.style.WARNING(f'User {user_data["username"]} already exists. Skipping creation.'))
                user = Member.objects.get(username=user_data['username'])
                created_users.append(user)
                continue
            
            # Create user
            user = Member.objects.create(
                username=user_data['username'],
                user_type='player',
            )
            user.set_password(user_data['password'])
            user.save()
            
            created_users.append(user)
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username} (referral code: {user.referral_code})'))
            
            # Create referral chain
            if i == 0:
                # First user is direct referral of Tim
                ReferralRelation.create_referral_chain(tim, user)
                self.stdout.write(f'  → Linked as direct referral of Tim (level 1)')
            else:
                # Each subsequent user is referral of the previous one
                referrer = created_users[i - 1]
                ReferralRelation.create_referral_chain(referrer, user)
                self.stdout.write(f'  → Linked as referral of {referrer.username} (level {i + 1} for Tim)')
        
        # Fund each user with 12000 rubles
        deposit_amount = Decimal('12000.00')
        
        for user in created_users:
            # Create deposit transaction
            transaction = Transaction.objects.create(
                member=user,
                type='deposit',
                amount=deposit_amount,
                currency='rubles',
                status='confirmed',
                description=f'Test deposit for analytics',
                confirmed_at=timezone.now()
            )
            
            # Update user balance
            user.balance_rubles += deposit_amount
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'Funded {user.username} with {deposit_amount} rubles (balance: {user.balance_rubles})'))
        
        # Simulate tournament participation and award bonuses
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('PROCESSING TOURNAMENT BONUSES:'))
        self.stdout.write('=' * 60)
        
        tim_total_bonuses = Decimal('0')
        
        for user in created_users:
            # Mark first tournament as played
            user.first_tournament_played = True
            user.save()
            
            self.stdout.write(f'\nProcessing first tournament for {user.username}...')
            
            # Award bonuses to referral chain (up to 10 levels)
            relations = ReferralRelation.objects.filter(
                referred=user
            ).select_related('referrer').order_by('level')
            
            for relation in relations:
                if relation.level == 1:
                    bonus_amount = relation.referrer.calculate_referral_bonus(user)
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
                    description=f"First tournament bonus from {user.username} (Level {relation.level})",
                    related_member=user,
                    confirmed_at=timezone.now()
                )
                
                # Update referrer balance
                if referrer_currency == 'vcoins':
                    relation.referrer.balance_vcoins += bonus_amount
                else:
                    relation.referrer.balance_rubles += bonus_amount
                relation.referrer.save()
                
                # Track Tim's bonuses
                if relation.referrer.id == tim.id:
                    tim_total_bonuses += bonus_amount
                
                self.stdout.write(
                    f'  → Awarded {bonus_amount} {referrer_currency} to {relation.referrer.username} '
                    f'(Level {relation.level} referral)'
                )
        
        # Display referral chain summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('REFERRAL CHAIN SUMMARY:'))
        self.stdout.write('=' * 60)
        
        tim_chain = ReferralRelation.objects.filter(referrer=tim).order_by('level', 'created_at')
        
        for relation in tim_chain:
            indent = '  ' * relation.level
            self.stdout.write(f'{indent}Level {relation.level}: {relation.referred.username} (balance: {relation.referred.balance_rubles} RUB)')
        
        # Refresh Tim from database
        tim.refresh_from_db()
        
        # Display Tim's bonus summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('TIM\'S BONUS SUMMARY:'))
        self.stdout.write('=' * 60)
        
        # Count bonuses by level
        bonus_by_level = {}
        tim_bonus_transactions = Transaction.objects.filter(
            member=tim,
            type='bonus',
            status='confirmed'
        ).select_related('related_member')
        
        for bonus in tim_bonus_transactions:
            if bonus.related_member:
                relation = ReferralRelation.objects.filter(
                    referrer=tim,
                    referred=bonus.related_member
                ).first()
                if relation:
                    level = relation.level
                    if level not in bonus_by_level:
                        bonus_by_level[level] = {'count': 0, 'amount': Decimal('0')}
                    bonus_by_level[level]['count'] += 1
                    bonus_by_level[level]['amount'] += bonus.amount
        
        for level in sorted(bonus_by_level.keys()):
            self.stdout.write(
                f'Level {level}: {bonus_by_level[level]["count"]} referrals, '
                f'{bonus_by_level[level]["amount"]} {"V-Coins" if tim.user_type == "player" else "rubles"}'
            )
        
        currency_display = 'V-Coins' if tim.user_type == 'player' else 'rubles'
        balance = tim.balance_vcoins if tim.user_type == 'player' else tim.balance_rubles
        
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write(self.style.SUCCESS(f'Total bonuses earned by Tim: {tim_total_bonuses} {currency_display}'))
        self.stdout.write(self.style.SUCCESS(f'Tim\'s current balance: {balance} {currency_display}'))
        self.stdout.write(self.style.SUCCESS(f'Total users in Tim\'s chain: {tim_chain.count()}'))
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\nTest data generation completed!'))


# Auto-execute the command
if __name__ == '__main__':
    call_command('seed_test_users')
