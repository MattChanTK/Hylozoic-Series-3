from setuptools import setup

setup(name='cbla',
      version='1.0',
      description='Core of the CBLA Algorithm',
      url='https://github.com/tuzzer/CBLA-Test-Bed',
      author='Matthew T.K. Chan',
      author_email='matthew.chan@uwaterloo.ca',
      license='MIT',
      packages=['cbla', 'cbla_engine'],
	  package_dir={'cbla': 'cbla', 'cbla_engine': 'cbla/cbla_engine'},
	  install_requires=[
          'interactive_system', 'abstract_node', 'sklearn', 'numpy'
      ],
      zip_safe=False)