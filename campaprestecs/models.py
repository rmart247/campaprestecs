# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class Usuari(AbstractUser):
    auth_token = models.CharField(max_length=32,blank=True,null=True)
    TIPUS_USUARI = [
        ('professor', 'Professor'),
        ('alumne', 'Alumne'),
        ('administrador', 'Administrador'),
    ]

    tipus_usuari = models.CharField(max_length=13, choices=TIPUS_USUARI, default='alumne', verbose_name="Tipus d'usuari")
    curs = models.CharField(max_length=50, blank=True, null=True, help_text="Obligatori només per a alumnes")
    
    def clean(self):
        super().clean()
        if self.tipus_usuari == 'alumne' and not self.curs:
            raise ValidationError({'curs': 'Els alumnes han de tenir un curs assignat.'})
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.tipus_usuari})"

    class Meta:
        verbose_name = "Usuari"
        verbose_name_plural = "Usuaris"

class Ordinador(models.Model):
    codi = models.CharField(max_length=50, unique=True, verbose_name="Codi de l'ordinador")
    model = models.CharField(max_length=100, blank=True, verbose_name="Model")
    data_adquisicio = models.DateField(blank=True, null=True, verbose_name="Data d'adquisició")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    
    def __str__(self):
        return f"{self.codi} ({'Disponible' if self.disponible else 'No disponible'})"

    class Meta:
        verbose_name = "Ordinador"
        verbose_name_plural = "Ordinadors"
        ordering = ['codi']

class Prestec(models.Model):
    professor_origen = models.ForeignKey(
        Usuari, 
        on_delete=models.PROTECT,
        related_name='prestecs_originats',
        limit_choices_to={'tipus_usuari': 'professor'},
        verbose_name="Professor que presta"
    )
    professor_destino = models.ForeignKey(
        Usuari, 
        on_delete=models.PROTECT,
        related_name='prestecs_rebuts',
        limit_choices_to={'tipus_usuari': 'professor'},
        blank=True, 
        null=True,
        verbose_name="Professor que rep en retornar"
    )
    alumne = models.ForeignKey(
        Usuari, 
        on_delete=models.PROTECT,
        related_name='prestecs_rebuts_alumne',
        limit_choices_to={'tipus_usuari': 'alumne'},
        verbose_name="Alumne que rep l'ordinador"
    )
    ordinador = models.ForeignKey(Ordinador, on_delete=models.PROTECT, verbose_name="Ordinador prestat")
    data_prestec = models.DateTimeField(auto_now_add=True, verbose_name="Data del préstec")
    data_retorn = models.DateTimeField(blank=True, null=True, verbose_name="Data de retorn")
    retornat = models.BooleanField(default=False, verbose_name="Retornat")
    observacions = models.TextField(blank=True, verbose_name="Observacions")
    
    class Meta:
        verbose_name = "Préstec"
        verbose_name_plural = "Préstecs"
        ordering = ['-data_prestec']
    
    def clean(self):
        if not self.ordinador.disponible and not self.retornat:
            raise ValidationError({'ordinador': 'Aquest ordinador no està disponible.'})
        
        if self.retornat and not self.data_retorn:
            self.data_retorn = timezone.now()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Actualitzar disponibilitat de l'ordinador
        if self.retornat:
            self.ordinador.disponible = True
        else:
            self.ordinador.disponible = False
        
        self.ordinador.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Préstec #{self.id} - {self.ordinador.codi} a {self.alumne.get_full_name()}"