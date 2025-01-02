#####
Chaos
#####

Playing with the ideas and images from the early days of chaos theory.

===========
Environment
===========

.. code-block::

   $ conda env create --name chaos-env --file environment.yml
   $ conda activate chaos-env

====
Test
====

.. code-block::

   $ pytest


===
Run
===

.. code-block::

   $ python main.py --initial 0.5 --parameter 1.0
