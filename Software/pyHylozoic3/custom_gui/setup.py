from setuptools import setup

setup(name='custom_gui',
      version='0.1',
      description='Custom GUI Framework for interacting with the interactive systems',
      url='https://github.com/tuzzer/CBLA-Test-Bed/',
      author='Matthew T.K. Chan',
      author_email='matthew.chan@uwaterloo.ca',
      license='MIT',
      packages=['custom_gui'],
	  package_dir={'custom_gui': 'custom_gui'},
	  install_requires=[
          'hmi_gui'
      ],
      zip_safe=False)