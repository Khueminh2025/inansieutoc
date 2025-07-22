# core/asset_utils.py

from .models import SiteAsset

def get_asset_url(key):
    """
    Lấy URL của ảnh trong SiteAsset theo key, nếu không có thì trả về None
    """
    # key = key.replace('-', '_')
    asset = SiteAsset.objects.filter(key=key).first()
    return asset.image.url if asset and asset.image else None
