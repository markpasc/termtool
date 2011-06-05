from distutils.core import setup


long_description = """
`termtool` helps you write subcommand-based command line tools in Python. It collects several Python libraries into a declarative syntax:

* :mod:`argparse`, the argument parsing module with subcommand support provided in the standard library in Python 2.7 and later.
* `prettytable <http://code.google.com/p/python-progressbar/>`_, an easy module for building tables of information.
* `progressbar <http://code.google.com/p/python-progressbar/>`_, a handy module for displaying progress bars.
* :mod:`logging`, the simple built-in module for logging messages.
"""


setup(
    name='termtool',
    version='1.0',
    description='Declarative terminal tool programming',
    author='Mark Paschal',
    author_email='markpasc@markpasc.org',
    url='https://github.com/markpasc/termtool',

    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],

    packages=[],
    py_modules=['termtool'],
    requires=['argparse', 'PrettyTable', 'progressbar'],
)
