# Generated by Django 5.1.6 on 2025-03-02 19:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_appointment_status_chatmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_new_patient',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Checked-In', 'Checked-In'), ('Chat Started', 'Chat Started'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_new_patient', models.BooleanField(default=True)),
                ('details', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.appointment')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.patient')),
            ],
        ),
    ]
