from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User, Notification
from posts.models import Post, Comment


class Command(BaseCommand):
    help = "Generate data for database performance benchmarking."

    def add_arguments(self, parser):
        parser.add_argument(
            "--posts",
            type=int,
            default=10000,
        )

        parser.add_argument(
            "--comments",
            type=int,
            default=20000,
        )

        parser.add_argument(
            "--notifications",
            type=int,
            default=10000,
        )

    @transaction.atomic
    def handle(self, *args, **options):

        post_count = options["posts"]
        comment_count = options["comments"]
        notification_count = options["notifications"]

        users = list(
            User.objects.filter(
                role=User.USER
            )
        )

        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR(
                    "At least 2 normal users are required."
                )
            )
            return

        self.stdout.write(
            "Creating performance dataset..."
        )

        posts = []

        for i in range(post_count):
            author = users[i % len(users)]

            posts.append(
                Post(
                    author=author,
                    title=f"Benchmark Post {i}",
                    content="Performance testing data.",
                )
            )

        Post.objects.bulk_create(
            posts,
            batch_size=1000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {post_count} posts."
            )
        )

        created_posts = list(
            Post.objects.order_by("-id")[:post_count]
        )

        comments = []

        for i in range(comment_count):
            post = created_posts[i % len(created_posts)]
            author = users[i % len(users)]

            comments.append(
                Comment(
                    post=post,
                    author=author,
                    content=f"Benchmark comment {i}",
                )
            )

        Comment.objects.bulk_create(
            comments,
            batch_size=1000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {comment_count} comments."
            )
        )

        notifications = []

        for i in range(notification_count):
            recipient = users[i % len(users)]
            actor = users[(i + 1) % len(users)]
            post = created_posts[i % len(created_posts)]

            notifications.append(
                Notification(
                    recipient=recipient,
                    actor=actor,
                    notification_type="LIKE",
                    post=post,
                )
            )

        Notification.objects.bulk_create(
            notifications,
            batch_size=1000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {notification_count} notifications."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Performance dataset created successfully."
            )
        )