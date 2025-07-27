# core/asset_utils.py

from .models import SiteAsset
from django.core.cache import cache

def get_asset_url(key):
    """
    Lấy URL của ảnh trong SiteAsset theo key, nếu không có thì trả về None
    """
    # key = key.replace('-', '_')
    cache_key = f"asset_url_{key}"
    asset = SiteAsset.objects.filter(key=key).first()
    url = cache.get(cache_key)

    if not url:
        asset = SiteAsset.objects.filter(key=key).first()
        url = asset.image.url if asset and asset.image else None
        cache.set(cache_key, url, 3600)  # cache trong 1 giờ
    return url
