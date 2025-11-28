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
        
        # Display referral chain summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('REFERRAL CHAIN SUMMARY:'))
        self.stdout.write('=' * 60)
        
        tim_chain = ReferralRelation.objects.filter(referrer=tim).order_by('level', 'created_at')
        
        for relation in tim_chain:
            indent = '  ' * relation.level
            self.stdout.write(f'{indent}Level {relation.level}: {relation.referred.username} (balance: {relation.referred.balance_rubles} RUB)')
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'\nTotal users in Tim\'s chain: {tim_chain.count()}'))
        self.stdout.write(self.style.SUCCESS('Test data generation completed!'))


# Auto-execute the command
if __name__ == '__main__':
    call_command('seed_test_users')
