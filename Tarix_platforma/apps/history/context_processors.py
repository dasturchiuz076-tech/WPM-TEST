from .models import Category


def categories_processor(request):
    """Return active categories for templates' global context."""
    try:
        categories = Category.objects.filter(is_active=True)
    except Exception:
        categories = []
    return {
        'categories': categories
    }