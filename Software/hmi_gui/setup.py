from setuptools import setup

setup(name='hmi_gui',
      version='0.1',
      description='GUI Framework for interacting with the interactive systems',
      url='https://github.com/tuzzer/CBLA-Test-Bed/',
      author='Matthew T.K. Chan',
      author_email='matthew.chan@uwaterloo.ca',
      license='MIT',
      packages=['hmi_gui'],
	  package_dir={'hmi_gui': 'hmi_gui'},
	  install_requires=[
          
      ],
      zip_safe=False)