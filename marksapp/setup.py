from setuptools import setup

setup(name='marksapp',
      version='0.1',
      description='program to store marks',
      license='MIT',
      packages=['marksapp'],
      install_requires=[
          'pyQt5',
          'cryptography',
          'argon2-cffi',
          'pandas',
          'numpy',
          'anytree',
          'classmarks',
      ],
      entry_points={"console_scripts": ["marksapp = marksapp.__main__:main"]},
      zip_safe=False)
