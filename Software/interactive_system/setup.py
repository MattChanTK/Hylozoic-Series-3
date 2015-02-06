from setuptools import setup

setup(name='interactive_system',
      version='0.3',
      description='Interface with Teensy control that control the interactive art sculpture at PBAI',
      url='https://github.com/tuzzer/CBLA-Test-Bed/tree/master/Software/InteractiveSystem',
      author='Matthew T.K. Chan',
      author_email='matthew.chan@uwaterloo.ca',
      license='MIT',
      packages=['interactive_system'],
	  package_dir={'interactive_system': 'interactive_system'},
      package_data={'interactive_system': ['protocol_config/*']},
	  install_requires=[
          'pyusb', 'numpy', 
      ],
      zip_safe=False)