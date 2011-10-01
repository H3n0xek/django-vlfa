from setuptools import setup, find_packages

setup(
    name = 'django-vlfa',
    version = '0.1b',
    description = 'Reusable forum application for the Django framework',
    long_description = ('Very Lite Forum Application. More advanced things are pluggable'),
    keywords = 'django forum apps',    
    author = 'H3n0xek and others (see AUTHORS file)',
    author_email = 'H3n0xek@blackhat.cc',
    url = 'http://github.com/H3n0xek/django-vlfa',
    license = 'GNU Lesser General Public License (LGPL), Version 3',
    classifiers = [
        'Environment :: Plugins',
        'Framework :: Django',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,    
)    

    