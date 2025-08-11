from django.conf import settings
from django.test import TestCase
from django.urls import reverse


from django_plugin_browser_reload import _inject_middleware


class TestDjangoPluginDebugToolbar(TestCase):
    def test_simple_view_works(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Hello world")

    def test_installed_apps_injected(self):
        self.assertIn("django_browser_reload", settings.INSTALLED_APPS)

    def test_toolbar_middleware_injected(self):
        self.assertEqual(
            settings.MIDDLEWARE,
            [
                "django.middleware.locale.LocaleMiddleware",
                "django.middleware.gzip.GZipMiddleware",
                "django_browser_reload.middleware.BrowserReloadMiddleware",
                "django.middleware.security.SecurityMiddleware",
            ],
        )

    def test_urls_added(self):
        _ = reverse("django_browser_reload:events")


class TestToolbarMiddlewareInjection(TestCase):
    def test_inject_middleware(self):
        test_cases = [
            {
                "description": "No middleware",
                "initial_middleware": [],
                "expected_middleware": [
                    "django_browser_reload.middleware.BrowserReloadMiddleware"
                ],
            },
            {
                "description": "Unknown middleware",
                "initial_middleware": ["a", "b"],
                "expected_middleware": [
                    "django_browser_reload.middleware.BrowserReloadMiddleware",
                    "a",
                    "b",
                ],
            },
            {
                "description": "Must go after GZipMiddleware",
                "initial_middleware": ["django.middleware.gzip.GZipMiddleware"],
                "expected_middleware": [
                    "django.middleware.gzip.GZipMiddleware",
                    "django_browser_reload.middleware.BrowserReloadMiddleware",
                ],
            },
            {
                "description": "Must go after GZipMiddleware even if it's preceeded by unknown middleware",
                "initial_middleware": ["a", "django.middleware.gzip.GZipMiddleware"],
                "expected_middleware": [
                    "a",
                    "django.middleware.gzip.GZipMiddleware",
                    "django_browser_reload.middleware.BrowserReloadMiddleware",
                ],
            },
            {
                "description": "Must go after GZipMiddleware but before following unknown middleware",
                "initial_middleware": [
                    "a",
                    "django.middleware.gzip.GZipMiddleware",
                    "b",
                ],
                "expected_middleware": [
                    "a",
                    "django.middleware.gzip.GZipMiddleware",
                    "django_browser_reload.middleware.BrowserReloadMiddleware",
                    "b",
                ],
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                initial_middleware = test_case["initial_middleware"]
                expected_middleware = test_case["expected_middleware"]
                self.assertEqual(
                    _inject_middleware(initial_middleware), expected_middleware
                )
