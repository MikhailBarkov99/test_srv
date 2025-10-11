"""Initial chat application migration."""
from __future__ import annotations

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create chat related tables."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_group', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='created_chats',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Chat',
                'verbose_name_plural': 'Chats',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='attachments/')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('chat', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to='chat.chat',
                )),
                ('sender', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('chat', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='chat_members',
                    to='chat.chat',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='chat_memberships',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Chat member',
                'verbose_name_plural': 'Chat members',
                'unique_together': {('chat', 'user')},
            },
        ),
        migrations.AddField(
            model_name='chat',
            name='members',
            field=models.ManyToManyField(related_name='chats', through='chat.ChatMember', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MessageRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='read_receipts',
                    to='chat.message',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='read_messages',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Message read receipt',
                'verbose_name_plural': 'Message read receipts',
                'unique_together': {('message', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['updated_at'], name='chat_chat_update_0e2d0f_idx'),
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['is_group'], name='chat_chat_is_group_7f6907_idx'),
        ),
        migrations.AddIndex(
            model_name='chatmember',
            index=models.Index(fields=['chat', 'user'], name='chat_chatme_chat_id_9e62e7_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['chat', 'created_at'], name='chat_messa_chat_id_3a1d3d_idx'),
        ),
        migrations.AddIndex(
            model_name='messageread',
            index=models.Index(fields=['user', 'read_at'], name='chat_messa_user_id_a44147_idx'),
        ),
    ]
