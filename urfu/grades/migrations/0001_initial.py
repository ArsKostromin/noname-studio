# Generated manually for initial migration

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('work_type', models.CharField(choices=[('homework', 'Домашняя работа'), ('test', 'Тест'), ('exam', 'Контрольная'), ('quiz', 'Мини-тест'), ('lab', 'Лабораторная'), ('project', 'Проект'), ('other', 'Другое')], max_length=20)),
                ('topic', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('value', models.IntegerField()),
                ('weight', models.FloatField(default=1.0)),
                ('is_final', models.BooleanField(default=False)),
                ('is_retake', models.BooleanField(default=False)),
                ('work_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='core.subject')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grades', to='core.teacher')),
            ],
        ),
    ]

