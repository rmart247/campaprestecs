# populate_db.py
import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from faker import Faker
from factory import django, fuzzy, LazyAttribute
from django.utils import timezone
from campaprestecs.models import Usuari, Ordinador, Prestec

# Configura Faker per a català i castellà
fake = Faker(["es_CA","es_ES"])

class UsuariFactory(django.DjangoModelFactory):
    class Meta:
        model = Usuari
    
    username = fuzzy.FuzzyText(length=8)
    first_name = LazyAttribute(lambda x: fake.first_name())
    last_name = LazyAttribute(lambda x: fake.last_name())
    email = LazyAttribute(lambda x: fake.email())
    tipus_usuari = fuzzy.FuzzyChoice(['professor', 'alumne'])
    curs = fuzzy.FuzzyChoice(['1r ESO', '2n ESO', '3r ESO', '4t ESO', '1r BATX', '2n BATX', '1r DAM', '2n DAM', '2n DAW', '2n SMX', '1r SMX'])
    
    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        if kwargs.get('tipus_usuari') != 'alumne':
            kwargs['curs'] = None
        return kwargs

class OrdinadorFactory(django.DjangoModelFactory):
    class Meta:
        model = Ordinador
    
    codi = fuzzy.FuzzyText(prefix='ORD-', length=6)
    model = fuzzy.FuzzyChoice(['Dell XPS 13', 'MacBook Pro', 'HP EliteBook', 'Lenovo ThinkPad', 'Asus ZenBook'])
    data_adquisicio = fuzzy.FuzzyDate(datetime(2018, 1, 1), datetime(2023, 12, 31))
    disponible = True

class Command(BaseCommand):
    help = 'Pobla la base de dades amb dades de prova'
    
    def add_arguments(self, parser):
        parser.add_argument('--usuaris', type=int, default=50, help='Nombre d\'usuaris a crear')
        parser.add_argument('--ordinadors', type=int, default=30, help='Nombre d\'ordinadors a crear')
        parser.add_argument('--prestecs', type=int, default=20, help='Nombre de préstecs a crear')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Començant a generar dades de prova...'))
        
        # Crear superusuari si no existeix
        if not Usuari.objects.filter(username='admin').exists():
            Usuari.objects.create_superuser(
                username='admin',
                email='admin@escola.cat',
                password='admin123',
                first_name='Admin',
                last_name='Sistema',
                tipus_usuari='administrador'
            )
            self.stdout.write(self.style.SUCCESS('Superusuari admin creat'))
        
        # Crear usuaris
        usuaris = UsuariFactory.create_batch(options['usuaris'])
        professors = [u for u in usuaris if u.tipus_usuari == 'professor']
        alumnes = [u for u in usuaris if u.tipus_usuari == 'alumne']
        
        self.stdout.write(self.style.SUCCESS(f'{len(usuaris)} usuaris creats'))
        
        # Crear ordinadors
        ordinadors = OrdinadorFactory.create_batch(options['ordinadors'])
        self.stdout.write(self.style.SUCCESS(f'{len(ordinadors)} ordinadors creats'))
        
        # Crear préstecs
        for _ in range(options['prestecs']):
            data_prestec = fake.date_time_between(start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone())
            data_retorn = None
            retornat = random.choice([True, False])
            
            if retornat:
                data_retorn = fake.date_time_between(start_date=data_prestec, end_date='now', tzinfo=timezone.get_current_timezone())
            
            prestec = Prestec.objects.create(
                professor_origen=random.choice(professors),
                professor_destino=random.choice(professors) if retornat else None,
                alumne=random.choice(alumnes),
                ordinador=random.choice(ordinadors),
                data_prestec=data_prestec,
                data_retorn=data_retorn,
                retornat=retornat,
                observacions=fake.sentence() if random.random() > 0.7 else ''
            )
            
            # Actualitzar disponibilitat de l'ordinador
            if not retornat:
                prestec.ordinador.disponible = False
                prestec.ordinador.save()
        
        self.stdout.write(self.style.SUCCESS(f'{options["prestecs"]} préstecs creats'))
        self.stdout.write(self.style.SUCCESS('Poblament de dades completat!'))