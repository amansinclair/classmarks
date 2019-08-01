from setuptools import setup

setup(name='classmarks',
      version='0.1',
      description='class marks sheet',
      license='MIT',
      packages=['classmarks'],
      install_requires=[
          'pandas',
          'numpy',
          'anytree'
      ],
      zip_safe=False)
