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

Example that "converges" to period 4

.. code-block::

   $ python main.py --initial 0.3 0.4 0.5 0.6 --parameter 3.4

Example of a multi-parameter study with periods 1, 2, and 4

.. code-block::

   $ python main.py --initial 0.25 --parameter 2 3.1 3.5

Begin exploring the bifurcation plot

.. code-block::

   $ python main.py --initial 0.25 --parameter 0.0 0.99 1.01 1.5 2.0 2.99 3.01 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8 3.9 4.0 --plot-bifurcation

Save the image

.. code-block::

   $ time python main.py --initial 0.25 --parameter 0.0 0.99 1.01 1.5 2.0 2.99 3.01 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8 3.9 4.0 --plot-bifurcation bifurcation.png

   real	0m4.462s
   user	0m5.096s
   sys	0m0.146s

.. image:: bifurcation.png

=====
Style
=====

.. code-block::

   $ black .
