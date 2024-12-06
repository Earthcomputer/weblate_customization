from os import environ as env
from weblate.settings_docker import *

ADMINS_CONTACT = ['burtonjae@hotmail.co.uk']
DEFAULT_COMMITER_EMAIL = 'translations@earthcomputer.net'
DEFAULT_COMMITER_NAME = 'Translations'
ENABLE_HTTPS = True
GET_HELP_URL = 'https://discord.gg/Jg7Bun7'
SIMPLIFY_LANGUAGES = False
SITE_DOMAIN = 'translations.earthcomputer.net'
SITE_TITLE = 'Earth\'s Translations'
AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.email.EmailAuth',
    'weblate.accounts.auth.WeblateUserBackend',
)

# TODO: fix email server
#EMAIL_HOST = 'mbox.freehostia.com'
#EMAIL_PORT = 993
#EMAIL_HOST_USER = 'translations@earthcomputer.net'
EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
SERVER_EMAIL = 'translations@earthcomputer.net'
DEFAULT_FROM_EMAIL = 'translations@earthcomputer.net'

SOCIAL_AUTH_GITHUB_KEY = env['AUTH_GITHUB_KEY']
SOCIAL_AUTH_GITHUB_SECRET = env['AUTH_GITHUB_SECRET']
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

#REGISTRATION_OPEN = False

INSTALLED_APPS = tuple(['weblate_customization'] + list(INSTALLED_APPS))

