from .models import PageVisit

# Statistikaga kirmaydigan yo'l boshlanmalari (admin, static, api va h.k.)
SKIP_PREFIXES = (
    '/admin', '/static', '/media', '/api',
    '/summernote', '/mdeditor', '/favicon',
)


def get_client_ip(request):
    """Proksi (nginx) ortidan haqiqiy IP ni aniqlaydi."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class VisitTrackingMiddleware:
    """Saytga tashriflarni (anonim mehmonlar ham) yozib boradigan middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._track(request, response)
        except Exception:
            # Statistika hech qachon saytni buzmasin
            pass
        return response

    def _track(self, request, response):
        # Faqat oddiy GET sahifa ko'rishlari
        if request.method != 'GET':
            return

        path = request.path
        if any(path.startswith(p) for p in SKIP_PREFIXES):
            return

        # Faqat muvaffaqiyatli HTML sahifalar
        if response.status_code != 200:
            return
        if 'text/html' not in response.get('Content-Type', ''):
            return

        # Anonim mehmonni noyob hisoblash uchun sessiya kaliti kerak
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        PageVisit.objects.create(
            session_key=session_key or '',
            ip_address=get_client_ip(request),
            user=request.user if request.user.is_authenticated else None,
            path=path[:500],
            referer=request.META.get('HTTP_REFERER', '')[:500],
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:400],
        )
