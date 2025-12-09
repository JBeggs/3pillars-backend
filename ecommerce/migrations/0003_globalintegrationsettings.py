# Generated manually for GlobalIntegrationSettings model

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0002_ecommercecompany_product_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalIntegrationSettings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_gateway', models.CharField(choices=[('yoco', 'Yoco'), ('payfast', 'PayFast'), ('paystack', 'PayStack'), ('stripe', 'Stripe')], default='yoco', help_text='Default payment gateway', max_length=50)),
                ('yoco_secret_key', models.CharField(blank=True, help_text='Global Yoco secret key (fallback for companies without their own)', max_length=255, null=True)),
                ('yoco_public_key', models.CharField(blank=True, help_text='Global Yoco public key', max_length=255, null=True)),
                ('yoco_webhook_secret', models.CharField(blank=True, help_text='Global Yoco webhook secret', max_length=255, null=True)),
                ('yoco_sandbox_mode', models.BooleanField(default=True, help_text='Global Yoco sandbox/test mode setting')),
                ('courier_service', models.CharField(choices=[('courier_guy', 'The Courier Guy'), ('pudo', 'Pudo (via Courier Guy)'), ('fastway', 'Fastway'), ('postnet', 'PostNet')], default='courier_guy', help_text='Default courier service', max_length=50)),
                ('courier_guy_api_key', models.CharField(blank=True, help_text='Global Courier Guy API key (fallback for companies without their own)', max_length=255, null=True)),
                ('courier_guy_api_secret', models.CharField(blank=True, help_text='Global Courier Guy API secret', max_length=255, null=True)),
                ('courier_guy_account_number', models.CharField(blank=True, help_text='Global Courier Guy account number', max_length=100, null=True)),
                ('courier_guy_sandbox_mode', models.BooleanField(default=True, help_text='Global Courier Guy sandbox/test mode setting')),
                ('payment_gateway_settings', models.JSONField(blank=True, default=dict, help_text='Additional global payment gateway settings')),
                ('courier_settings', models.JSONField(blank=True, default=dict, help_text='Additional global courier service settings')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Global Integration Settings',
                'verbose_name_plural': 'Global Integration Settings',
            },
        ),
    ]

