from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.utils.html import format_html
from django.db.models import Count

# Register your models here.
from .models import Usuari, Ordinador, Prestec

class UserInline(admin.StackedInline):
    model = Usuari
    extra = 3
    #fieldsets = [("Informació d'usuari", {"fields": ["auth_token","tipus_usuari"], 'collapse': True}),]


#prova de creació de vista personalitzada


class CursFilter(admin.SimpleListFilter):
    title = 'Curs'  # Títol del filtre
    parameter_name = 'curs'  # Paràmetre URL per al filtre

    def lookups(self, request, model_admin):
        # Obtenim tots els cursos únics dels alumnes
        cursos = Usuari.objects.exclude(curs__isnull=True).order_by('curs').values_list('curs', flat=True).distinct()
        return [(curs, curs) for curs in cursos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(curs=self.value())
        return queryset

class UsuariAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'tipus_usuari', 'curs', 'is_active')
    list_filter = (CursFilter, 'tipus_usuari', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'curs')
    ordering = ('curs', 'last_name', 'first_name')
    
    # Afegim un camp calculat per al nom complet
    def full_name(self, obj):
        return f"{obj.last_name}, {obj.first_name}"
    full_name.short_description = 'Nom complet'
    full_name.admin_order_field = 'last_name'
    
    # Sobreescrivim el changelist_view per afegir estadístiques
    def changelist_view(self, request, extra_context=None):
        # Obtenim les estadístiques per curs
        stats = Usuari.objects.filter(tipus_usuari='alumne').values('curs').annotate(
            total=Count('id')
        ).order_by('curs')
        
        # Agrupem usuaris per curs
        usuaris_per_curs = {}
        for stat in stats:
            curs = stat['curs']
            usuaris = Usuari.objects.filter(curs=curs).order_by('last_name', 'first_name')
            usuaris_per_curs[curs] = {
                'total': stat['total'],
                'usuaris': usuaris
            }
        
        # Afegim les dades al context
        extra_context = extra_context or {}
        extra_context['stats'] = stats
        extra_context['usuaris_per_curs'] = usuaris_per_curs
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Usuari, UsuariAdmin)
admin.site.register(Ordinador)
admin.site.register(Prestec)