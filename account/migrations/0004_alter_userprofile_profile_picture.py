# Generated by Django 4.2.6 on 2023-10-30 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='photos/userprofile/default-avatar.png', upload_to='photos/userprofile/'),
        ),
    ]
