# This file is to load default Users and other datas for testing the program
from django.core.management.base import BaseCommand
from accounts.models import User
from posts.models import Post

class Command(BaseCommand):

    help = "Create default users and posts for development/testing."


    def handle(self, *args, **options):

        # -------------------------
        # Admin
        # -------------------------

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@userhub.local",
                "role": User.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            }
        )

        if created:
            admin.set_password("Admin12345")
            admin.save()

            self.stdout.write(
                self.style.SUCCESS(
                    "Created admin user."
                )
            )

        else:
            self.stdout.write(
                "Admin already exists."
            )


        # -------------------------
        # Normal Users
        # -------------------------

        users = []

        for number in range(1, 7):

            username = f"testuser{number}"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@userhub.local",
                    "role": User.USER,
                }
            )

            if created:

                user.set_password("Test12345")
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {username}."
                    )
                )

            users.append(user)


        # -------------------------
        # Posts
        # -------------------------

        post_count = 0

        for user in users:

            for number in range(1, 5):

                title = (
                    f"{user.username} Post {number}"
                )

                post, created = Post.objects.get_or_create(
                    title=title,
                    defaults={
                        "author": user,
                        "content": (
                            f"This is test post "
                            f"{number} created by "
                            f"{user.username}."
                        ),
                    }
                )

                if created:
                    post_count += 1


        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Seed data completed successfully."
            )
        )

        self.stdout.write(
            f"Admin: admin / Admin12345"
        )

        self.stdout.write(
            f"Test users: testuser1 ... testuser6"
        )

        self.stdout.write(
            f"Test user password: Test12345"
        )

        self.stdout.write(
            f"Created posts: {post_count}"
        )