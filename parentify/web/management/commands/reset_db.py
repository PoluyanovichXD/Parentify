from django.core.management.base import BaseCommand, CommandError
from parentify.models import *
from parentify.methods.add_super_admin import add_super_admin
from sqlalchemy.orm.session import object_session

class Command(BaseCommand):
    help = 'Reset database - drop all tables and recreate them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        if not force:
            confirm = input(
                "⚠️  WARNING: This will DROP ALL TABLES and lose all data!\n"
                "Are you sure you want to reset the database? (yes/no): "
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Database reset cancelled.'))
                return

        try:
            self.stdout.write("Dropping all tables...")
            
            Base.metadata.drop_all(engine)
            
            self.stdout.write(self.style.SUCCESS("All tables dropped successfully"))
            
            self.stdout.write("Creating all tables...")
            Base.metadata.create_all(engine)
            
            self.stdout.write(self.style.SUCCESS("Database structure recreated successfully"))
            
            self.stdout.write("Adding default data...")
            orm = Orm()
            add_super_admin(orm,"parentify.official@gmail.com", 'Администратор', 'Parentify', "parentify.official1111")
            orm.close()
            
            self.stdout.write(self.style.SUCCESS("Database reset and initialized successfully!"))
            
        except Exception as e:
            raise CommandError(f"Error resetting database: {e}")