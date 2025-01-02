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

Example that converges pretty quickly

.. code-block::

   $ python main.py --initial 0.3 0.4 0.5 0.6 --parameter 2.4

Example that "converges" to period 2 (bouncing between two states)

.. code-block::

   $ python main.py --initial 0.3 0.4 0.5 0.6 --parameter 3.1

Example that "converges" to period 2 in more than 100 iterations

.. code-block::

   $ python main.py --initial 0.3 0.4 0.5 0.6 --parameter 3 -m 1000

=====
Style
=====

.. code-block::

   $ black .
