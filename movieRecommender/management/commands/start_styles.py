from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    help = 'Start Server with tailwind css styles'

    def handle(self, *args, **options):
        install_tailwind = 'python manage.py tailwind install'
        start_tailwind = 'python manage.py tailwind start'
        try:
            subprocess.run(install_tailwind + ' && ' +
                           start_tailwind, shell=True)
        except:
            self.stdout.write(self.style.SUCCESS(
                '\n Servidor de Tailwind detenido.'))
