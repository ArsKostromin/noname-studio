# Generated manually for initial migration

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('weekday', models.IntegerField()),
                ('starts_at', models.TimeField()),
                ('ends_at', models.TimeField()),
                ('room', models.CharField(blank=True, max_length=100, null=True)),
                ('topic', models.CharField(blank=True, help_text='Тема занятия', max_length=255, null=True)),
                ('group_related_topics', models.JSONField(blank=True, help_text='Темы группы на этой паре', null=True)),
                ('max_score', models.FloatField(default=0.0)),
                ('is_control_work', models.BooleanField(default=False)),
                ('is_test', models.BooleanField(default=False)),
                ('is_exam', models.BooleanField(default=False)),
                ('is_lab_work', models.BooleanField(default=False)),
                ('is_final', models.BooleanField(default=False)),
                ('is_retake', models.BooleanField(default=False)),
                ('materials_link', models.URLField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='core.group')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='core.subject')),
                ('teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='classes', to='core.teacher')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='schedule',
            unique_together={('subject', 'group', 'weekday', 'starts_at')},
        ),
    ]

