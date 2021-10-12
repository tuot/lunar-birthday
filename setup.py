import pathlib
import pkg_resources

from setuptools import find_packages, setup

with pathlib.Path('requirements.txt').open() as fp:
    install_requires = [
        str(requirement) for requirement in pkg_resources.parse_requirements(fp)
    ]

setup(name='lunar_birthday',
      version='2.0',
      description='Lunar Birthday to Google Calendar',
      author='tuo',
      author_email='',
      url='https://github.com/tuot',
      packages=find_packages(),
      keywords=['google', 'lunar birthday', 'calendar', 'google calendar'],
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              'lb=lunar_birthday.command:main',
          ],
      }
      )
