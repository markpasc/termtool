from setuptools import setup

setup(
    name='termtool',
    version='1.0',
    packages=[],
    include_package_data=True,
    modules=['termtool.py'],

    requires=['argparse', 'PrettyTable', 'progressbar'],
    install_requires=['argparse', 'PrettyTable', 'progressbar'],
)
