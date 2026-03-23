from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Priority, Category, Task, SubTask, Note
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with Priority, Category, Task, SubTask, and Note records'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # ── Priorities (manually added per spec) ──────────────────────────────
        priorities = ['High', 'Medium', 'Low', 'Critical', 'Optional']
        priority_objects = []
        for name in priorities:
            obj, created = Priority.objects.get_or_create(name=name)
            priority_objects.append(obj)
            if created:
                self.stdout.write(f'  Created Priority: {name}')

        # ── Categories (manually added per spec) ──────────────────────────────
        categories = ['Work', 'School', 'Personal', 'Finance', 'Projects']
        category_objects = []
        for name in categories:
            obj, created = Category.objects.get_or_create(name=name)
            category_objects.append(obj)
            if created:
                self.stdout.write(f'  Created Category: {name}')

        # ── Tasks (faker generated) ────────────────────────────────────────────
        statuses = ["Pending", "In Progress", "Completed"]
        task_objects = []
        for _ in range(20):
            task = Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                status=fake.random_element(elements=statuses),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                category=random.choice(category_objects),
                priority=random.choice(priority_objects),
            )
            task_objects.append(task)

        self.stdout.write(f'  Created {len(task_objects)} Tasks')

        # ── SubTasks (faker generated) ─────────────────────────────────────────
        subtask_count = 0
        for task in task_objects:
            for _ in range(random.randint(1, 4)):
                SubTask.objects.create(
                    parent_task=task,
                    title=fake.sentence(nb_words=4),
                    status=fake.random_element(elements=statuses),
                )
                subtask_count += 1

        self.stdout.write(f'  Created {subtask_count} SubTasks')

        # ── Notes (faker generated) ────────────────────────────────────────────
        note_count = 0
        for task in task_objects:
            for _ in range(random.randint(0, 3)):
                Note.objects.create(
                    task=task,
                    content=fake.paragraph(nb_sentences=2),
                )
                note_count += 1

        self.stdout.write(f'  Created {note_count} Notes')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
