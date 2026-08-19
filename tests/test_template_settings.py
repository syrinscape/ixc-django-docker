from copy import deepcopy
from unittest import TestCase, main

from ixc_django_docker.template_settings import apply_legacy_template_settings


class ApplyLegacyTemplateSettingsTests(TestCase):
    def setUp(self):
        self.django_backend = {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ('base-templates',),
            'OPTIONS': {
                'context_processors': ('base.context_processor',),
                'loaders': ('base.Loader',),
            },
        }
        self.jinja_backend = {
            'BACKEND': 'django.template.backends.jinja2.Jinja2',
            'DIRS': ('jinja2',),
            'OPTIONS': {},
        }

    def test_applies_project_legacy_settings_and_preserves_jinja(self):
        settings = {
            'TEMPLATES': [self.django_backend, self.jinja_backend],
            'TEMPLATE_DIRS': ('project-templates',),
            'TEMPLATE_LOADERS': ('project.Loader',),
            'TEMPLATE_CONTEXT_PROCESSORS': (
                'django.core.context_processors.request',
                'project.context_processor',
            ),
        }
        original_jinja_backend = deepcopy(self.jinja_backend)

        apply_legacy_template_settings(settings, (1, 8, 19, 'final', 0))

        self.assertEqual(self.django_backend['DIRS'], ('project-templates',))
        self.assertEqual(
            self.django_backend['OPTIONS']['loaders'],
            ('project.Loader',),
        )
        self.assertEqual(
            self.django_backend['OPTIONS']['context_processors'],
            (
                'django.template.context_processors.request',
                'project.context_processor',
            ),
        )
        self.assertEqual(self.jinja_backend, original_jinja_backend)

    def test_applies_legacy_settings_to_sparse_aliased_backend(self):
        django_backend = {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
        }
        settings = {
            'TEMPLATES': [django_backend],
            'TEMPLATE_LOADERS': ('project.Loader',),
            'TEMPLATE_CONTEXT_PROCESSORS': (
                'django.core.context_processors.request',
                'project.context_processor',
            ),
        }

        apply_legacy_template_settings(settings, (1, 8, 19, 'final', 0))

        self.assertIs(settings['TEMPLATES'][0], django_backend)
        self.assertEqual(
            django_backend['OPTIONS'],
            {
                'loaders': ('project.Loader',),
                'context_processors': (
                    'django.template.context_processors.request',
                    'project.context_processor',
                ),
            },
        )

    def test_does_not_create_options_without_legacy_option_settings(self):
        django_backend = {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
        }
        settings = {
            'TEMPLATES': [django_backend],
            'TEMPLATE_DIRS': ('project-templates',),
        }

        apply_legacy_template_settings(settings, (1, 8, 19, 'final', 0))

        self.assertIs(settings['TEMPLATES'][0], django_backend)
        self.assertEqual(
            django_backend,
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ('project-templates',),
            },
        )

    def test_does_not_apply_legacy_settings_outside_django_18_and_19(self):
        for django_version in ((1, 7), (1, 10)):
            django_backend = deepcopy(self.django_backend)
            settings = {
                'TEMPLATES': [django_backend],
                'TEMPLATE_DIRS': ('project-templates',),
            }

            apply_legacy_template_settings(settings, django_version)

            self.assertEqual(django_backend['DIRS'], ('base-templates',))


if __name__ == '__main__':
    main()
