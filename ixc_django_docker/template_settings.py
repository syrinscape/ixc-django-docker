DJANGO_TEMPLATES_BACKEND = (
    'django.template.backends.django.DjangoTemplates'
)


def apply_legacy_template_settings(settings, django_version):
    """Apply final legacy template settings to Django 1.8/1.9 backends."""
    if not (1, 8) <= django_version < (1, 10):
        return

    for template_backend in settings.get('TEMPLATES', ()):
        if template_backend['BACKEND'] != DJANGO_TEMPLATES_BACKEND:
            continue

        if 'TEMPLATE_DIRS' in settings:
            template_backend['DIRS'] = settings['TEMPLATE_DIRS']
        if 'TEMPLATE_LOADERS' in settings:
            options = template_backend.setdefault('OPTIONS', {})
            options['loaders'] = settings['TEMPLATE_LOADERS']
        if 'TEMPLATE_CONTEXT_PROCESSORS' in settings:
            options = template_backend.setdefault('OPTIONS', {})
            context_processors = settings['TEMPLATE_CONTEXT_PROCESSORS']
            translated_context_processors = (
                _translate_context_processor(path)
                for path in context_processors
            )
            options['context_processors'] = (
                tuple(translated_context_processors)
                if isinstance(context_processors, tuple)
                else list(translated_context_processors)
            )
        break


def _translate_context_processor(path):
    old_prefix = 'django.core.context_processors.'
    if path.startswith(old_prefix):
        return 'django.template.context_processors.' + path[len(old_prefix):]
    return path
