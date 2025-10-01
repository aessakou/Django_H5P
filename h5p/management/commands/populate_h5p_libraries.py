from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Populate H5P libraries into the system'

    def handle(self, *args, **kwargs):
        # Your logic here
        self.stdout.write(self.style.SUCCESS('H5P libraries populated!'))
