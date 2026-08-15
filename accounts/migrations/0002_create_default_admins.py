from django.db import migrations


def create_admins(apps, schema_editor):

    User = apps.get_model(
        'accounts',
        'User'
    )


    if not User.objects.exists():

        User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
            role="ADMIN"
        )


        User.objects.create_superuser(
            username="manager",
            email="manager@test.com",
            password="manager123",
            role="ADMIN"
        )


def remove_admins(apps, schema_editor):
    pass



class Migration(migrations.Migration):

    dependencies = [
        ('accounts','0001_initial'),
    ]


    operations = [
        migrations.RunPython(
            create_admins,
            remove_admins
        )
    ]