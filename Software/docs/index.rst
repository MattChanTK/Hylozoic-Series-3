.. Hylozoic Series 3 documentation master file, created by
   sphinx-quickstart on Thu Jan 28 16:36:26 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Hylozoic Series 3's documentation!
=============================================

**pyHylozoic3** is a set of Python modules that provide the key features introduced in the Hylozoic Series 3 system. 

- interactive_system_ provides the infrastructures that enable a client running a pyHylozoic3 program to communicate with a distributed set of microconstrollers.

- abstract_node_ enables the creation of a network of asychronous threads that describe the behaviour of the system.

- hmi_gui_ provides a basic GUI that is compatible the *abstract_node* system.

- custom_gui_ provides a set of customized GUI based on *hmi_gui* that tailors to a handful of operation modes.

- cbla_ contains the CBLA Engine and the implementation of a generic CBLA Node.

.. _interactive_system: ./_apidoc/interactive_system/modules.html
.. _abstract_node: ./_apidoc/abstract_node/modules.html
.. _hmi_gui: ./_apidoc/hmi_gui/modules.html
.. _custom_gui: ./_apidoc/custom_gui/modules.html
.. _cbla: ./_apidoc/cbla/modules.html

**complex_behaviours** contains a handful of specific implementations that use the *pyHylozoic3* Module.

- *pbai_fin_test_bed* contains the implementation of manual, prescipted, and CBLA type behaviours for the CBLA Fin Test Bed.

- *cbla_test_bed* contains the implementation of CBLA behaviours for the CBLA Test Bed used during development and validation of the CBLA. This behaviour does not use the *cbla* module in *pyHylozoic3*. Instead, its CBLA Engine and CBLA Nodes are embedded to protect the integrity of the system.

- *washington_demo* contains the work-in-progress for the Sound Test Bed that is primarily used for demostration purposes in Washington and perhaps CITA.

Contents:

.. toctree::
   :maxdepth: 2
   
   ./installing

Communications Protocol
=======================
There is no standard protocol because every configuration has a different set of hardware attached.
So for each installation, we would need to write a different set of protocols.
   
Terminology
===========
Nodes are hierarchial and can comprise of other nodes (i.e. nodes can be sets of nodes).
But at their most basic level each sensor or actuator can be its own node and nodes can consist of inputs and/or outputs.
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

