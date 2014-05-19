from setuptools import setup, find_packages

setup(
    name='PO-Projects-client',
    version=__import__('po_projects_client').__version__,
    description=__import__('po_projects_client').__doc__,
    long_description=open('README.rst').read(),
    author='David Thenon',
    author_email='dthenon@emencia.com',
    url='http://pypi.python.org/pypi/PO-Projects-client',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'nap >= 1.0.0',
        'pkginfo >= 1.2b1',
        'argparse==1.2.1',
        'argcomplete==0.8.0',
        'argh==0.24.1',
    ],
    entry_points={
        'console_scripts': [
            'po_projects = po_projects_client.cli:main',
        ]
    },
    include_package_data=True,
    zip_safe=False
)