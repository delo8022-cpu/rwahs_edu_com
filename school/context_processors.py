from .models import LinkCategory, Official, SiteSettings, BreakingNews

def sidebar_context(request):
    categories = LinkCategory.objects.prefetch_related('sidebarlink_set').filter(
        sidebarlink__is_active=True
    ).distinct()
    officials = Official.objects.all()
    return {
        'sidebar_categories': categories,
        'sidebar_officials': officials,
    }

def site_settings(request):
    return {'site_settings': SiteSettings.load()}

def global_context(request):
    return {
        'breaking_news': BreakingNews.objects.filter(is_active=True).order_by('order'),
    }