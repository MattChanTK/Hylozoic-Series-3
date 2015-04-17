from setuptools import setup

setup(name='abstract_node',
      version='0.3',
      description='An abstraction of a node with a set of inputs and output variables',
      url='https://github.com/tuzzer/CBLA-Test-Bed/',
      author='Matthew T.K. Chan',
      author_email='matthew.chan@uwaterloo.ca',
      license='MIT',
      packages=['abstract_node'],
	  package_dir={'abstract_node': 'abstract_node'},
	  install_requires=[
          'interactive_system',
      ],
      zip_safe=False)