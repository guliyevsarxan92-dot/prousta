from .models import Profil

def create_profil(backend, user, response, *args, **kwargs):
    profil, yaradildi = Profil.objects.get_or_create(istifadeci=user)
    if yaradildi:
        profil.ad = user.first_name or ''
        profil.soyad = user.last_name or ''
        profil.save()
