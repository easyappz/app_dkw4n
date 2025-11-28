# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('password_hash', models.CharField(max_length=128)),
                ('user_type', models.CharField(choices=[('player', 'Player'), ('influencer', 'Influencer')], default='player', max_length=20)),
                ('referral_code', models.CharField(db_index=True, max_length=20, unique=True)),
                ('balance_vcoins', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('balance_rubles', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('level', models.CharField(choices=[('none', 'None'), ('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum')], default='none', max_length=20)),
                ('is_admin', models.BooleanField(default=False)),
                ('first_tournament_played', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'members',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum')], max_length=20, unique=True)),
                ('required_referrals', models.IntegerField(default=0)),
                ('bonus_multiplier', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
            ],
            options={
                'db_table': 'levels',
                'ordering': ['required_referrals'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('bonus', 'Bonus'), ('tournament', 'Tournament')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(choices=[('vcoins', 'V-Coins'), ('rubles', 'Rubles')], max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='api.member')),
                ('related_member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_transactions', to='api.member')),
            ],
            options={
                'db_table': 'transactions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReferralRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referred', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to='api.member')),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals_made', to='api.member')),
            ],
            options={
                'db_table': 'referral_relations',
                'ordering': ['level', '-created_at'],
                'unique_together': {('referrer', 'referred')},
            },
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['member', '-created_at'], name='transaction_member__idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['type', 'status'], name='transaction_type_idx'),
        ),
        migrations.AddIndex(
            model_name='referralrelation',
            index=models.Index(fields=['referrer', 'level'], name='referral_re_referre_idx'),
        ),
        migrations.AddIndex(
            model_name='referralrelation',
            index=models.Index(fields=['referred'], name='referral_re_referre_idx2'),
        ),
    ]
