

from slugify import slugify


def unique_slugify(instance, value, slug_field_name='slug'):
    """
    Tạo slug duy nhất cho instance từ value (thường là name).
    Tự động thêm -1, -2, ... nếu slug đã tồn tại.
    """
    base_slug = slugify(value)
    slug = base_slug
    counter = 1
    ModelClass = instance.__class__

    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


