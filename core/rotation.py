from django.db import connection
from django.db.models import F, TextField, Value, Case, When, IntegerField
from django.utils import timezone
from django.db.models.functions import MD5, Cast, Concat


def apply_fair_rotation(qs, seed):
    """
    Ədalətli göstərim / rotasiya sistemi:
    1. Əgər 'is_local' qeyd edilibsə, həmin əraziyə uyğun elanlar ən öndə
    2. Super VIP (vip_siralama=2) ən öndə
    3. VIP (vip_siralama=1) növbəti
    4. Normal elanlar (vip_siralama=0) sonra
    Hər status daxilində elanlar seed əsasında psövdo-təsadüfi (MD5 hash)
    ədalətli rotasiya ilə paylanır.
    """
    seed = str(seed)[:64]
    has_local = 'is_local' in getattr(qs.query, 'annotations', {})
    order_fields = []
    if has_local:
        order_fields.append(F('is_local').desc())
    qs = qs.alias(_effective_vip_rank=Case(
        When(vip_status__in=['vip', 'super_vip'], vip_bitis__gt=timezone.now(), then=Value(1)),
        default=Value(0), output_field=IntegerField()))
    order_fields.append(F('_effective_vip_rank').desc())
    order_fields.append(F('ireli_cekildi').desc(nulls_last=True))

    if connection.vendor == 'postgresql':
        return qs.annotate(
            _seed_hash=MD5(Concat(Cast('id', TextField()), Value(f':{seed}'), output_field=TextField()))
        ).order_by(
            *order_fields,
            '_seed_hash',
            F('yaradildi').desc(),
        )
    return qs.order_by(
        *order_fields,
        F('vip_yenilendi').desc(nulls_last=True),
        F('yaradildi').desc(),
    )

