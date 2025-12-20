from django.core.management.base import BaseCommand, CommandError
from parentify.models         import *
from parentify.methods.add_super_admin import add_super_admin
from sqlalchemy.orm.session         import object_session
class Command(BaseCommand):

    def handle(self, *args, **options):
        Base.metadata.create_all(engine)
        self.stdout.write(self.style.SUCCESS("DataBase is initialized"))
        orm = Orm()
        add_super_admin(orm,"parentify.official@gmail.com", 'Администратор', 'Parentify', "parentify.official1111")
        orm.close()
        