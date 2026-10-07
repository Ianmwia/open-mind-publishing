import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from projects.models import Project, ProjectCategory, ProjectType, ProjectStatus, ProjectAssignment, AssignmentRole
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Import projects from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to Excel file')
        parser.add_argument('--admin-username', type=str, default='admin', help='Username to assign as created_by')

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        admin_username = options['admin_username']

        self.stdout.write(f'Reading Excel file: {excel_file}')

        # Read Excel file
        df = pd.read_excel(excel_file, header=1, skiprows=[0])
        df.columns = ['Title', 'ISBN', 'Authors', 'Language', 'Level', 'Status']

        # Clean data - remove rows with invalid data
        df = df[df['Title'] != 'Indeginous  readers']  # Remove header row
        df = df[df['Status'] != 'Status']  # Remove duplicate header
        df = df[df['Language'] != 'Language']  # Remove duplicate header
        df = df.dropna(subset=['Title'])  # Remove rows without title

        self.stdout.write(f'Found {len(df)} valid projects to import')

        # Get or create admin user
        try:
            admin_user = CustomUser.objects.get(username=admin_username)
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Admin user "{admin_username}" not found. Creating...'))
            admin_user = CustomUser.objects.create_user(
                username=admin_username,
                email=f'{admin_username}@openmind.com',
                password='temp123',  # Change this after import
                is_staff=True,
                is_superuser=True
            )

        # Import projects
        with transaction.atomic():
            for idx, row in df.iterrows():
                title = row['Title']
                isbn = row['ISBN'] if pd.notna(row['ISBN']) else ''
                authors = row['Authors'] if pd.notna(row['Authors']) else ''
                language = row['Language'] if pd.notna(row['Language']) else ''
                level = row['Level'] if pd.notna(row['Level']) else ''
                status = row['Status'] if pd.notna(row['Status']) else ''

                # Map Excel status to ProjectStatus
                status_mapping = {
                    'Completed': ProjectStatus.PUBLISHED,
                    'Incomplete': ProjectStatus.IDEA,
                    'WIP': ProjectStatus.DRAFTING,
                }
                project_status = status_mapping.get(status, ProjectStatus.IDEA)

                # Determine category and type based on language
                if 'English' in language or language == 'English':
                    category = ProjectCategory.DIGITAL
                    project_type = ProjectType.ENGLISH_STORYBOOK
                elif '-' in language or 'English' in language:
                    category = ProjectCategory.LANGUAGE
                    project_type = ProjectType.BILINGUAL_READER
                else:
                    category = ProjectCategory.LANGUAGE
                    project_type = ProjectType.BILINGUAL_READER

                # Handle bilingual languages
                if '-' in language:
                    lang_parts = language.split('-')
                    primary_lang = lang_parts[0].strip()
                    secondary_lang = lang_parts[1].strip() if len(lang_parts) > 1 else 'English'
                else:
                    primary_lang = language if language else 'English'
                    secondary_lang = ''

                # Check if project already exists
                if Project.objects.filter(title=title).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate: {title}'))
                    continue

                # Create project
                project = Project.objects.create(
                    title=title,
                    description=f'Authors: {authors}\nLevel: {level}',
                    category=category,
                    project_type=project_type,
                    status=project_status,
                    primary_language=primary_lang,
                    secondary_language=secondary_lang,
                    isbn_or_sku=str(isbn),
                    target_age_group=f'Level {level}' if level else '',
                    created_by=admin_user,
                    is_published=(status == 'Completed')
                )

                # Assign authors to project
                if authors:
                    author_names = [name.strip() for name in authors.split(',')]
                    for author_name in author_names:
                        if not author_name:
                            continue

                        # Try to find existing user by username or pen_name
                        user = None
                        try:
                            user = CustomUser.objects.get(username=author_name)
                        except CustomUser.DoesNotExist:
                            try:
                                user = CustomUser.objects.get(pen_name=author_name)
                            except CustomUser.DoesNotExist:
                                # Create new user
                                username = author_name.replace(' ', '_').lower()
                                username = ''.join(c for c in username if c.isalnum() or c == '_')
                                base_username = username
                                counter = 1
                                while CustomUser.objects.filter(username=username).exists():
                                    username = f'{base_username}_{counter}'
                                    counter += 1

                                user = CustomUser.objects.create_user(
                                    username=username,
                                    email=f'{username}@openmind.com',
                                    password='temp123',  # Users will need to reset
                                    pen_name=author_name
                                )
                                self.stdout.write(self.style.SUCCESS(f'Created user: {author_name} ({username})'))

                        # Assign user to project as author
                        if user:
                            ProjectAssignment.objects.get_or_create(
                                project=project,
                                user=user,
                                role=AssignmentRole.AUTHOR,
                                defaults={'deliverable_notes': f'Imported from Excel'}
                            )

                self.stdout.write(self.style.SUCCESS(f'Imported: {title}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully imported projects!'))
