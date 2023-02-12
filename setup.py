from setuptools import setup, find_packages

VERSION = "0.0.2"
DESCRIPTION = "Azure Comunication Service Email Backend for Django"
LONG_DESCRIPTION = "Package to send emails using Azure Communication Service from Django using a BackendEmail."

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="django_acs_email",
    version=VERSION,
    author="Juan Carlos Espinoza Zurita",
    author_email="carlos_jcez@hotmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["azure-communication-email"],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    keywords=[
        "python",
        "django",
        "azure",
        "communication",
        "service",
        "email",
        "backend",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 4.0",
    ],
)
