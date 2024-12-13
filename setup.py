from setuptools import setup

setup(
    name="weblate_customization",
    version="0.0.1",
    author="Earthcomputer",
    author_email="burtonjae@hotmail.co.uk",
    description="Weblate Customization",
    license="MIT",
    keywords="Weblate check",
    packages=["weblate_customization"],
    package_data={"weblate_customization": ["static/**", "templates/**"]},
)

