from setuptools import setup, find_packages

setup(name='lunar_birthday',
      version='1.0',
      description='Lunar Birthday to Google Calendar',
      author='tuo',
      author_email='iooicoder@gmail.com',
      url='https://github.com/tuot',
      packages=find_packages(),
      keywords=['google', 'lunar birthday', 'calendar', 'google calendar'],
      install_requires=[
          'google-api-python-client==1.7.8',
          'oauth2client==4.1.3',
          'zhdate==0.1',
      ],
      entry_points={
          "console_scripts": [
              "lb=lunar_birthday.cmd:main",
          ],
      }
      )
