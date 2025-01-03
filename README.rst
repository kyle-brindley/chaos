#####
Chaos
#####

Playing with the ideas and images from the early days of chaos theory.

=====
Clone
=====

.. code-block::

   $ git clone git@github.com:kyle-brindley/chaos.git

===========
Environment
===========

.. code-block::

   $ conda env create --name chaos-env --file environment.yml
   $ conda activate chaos-env

===
Run
===

This project can be run directly from the repository with the commands below.
Alternately, use a ``pip`` editable install, ``pip install -e .``, and run as
an executable with ``chaos`` instead of ``python chaos.main``.

Example that converges pretty quickly

.. code-block::

   $ python chaos.main --initial 0.3 0.4 0.5 0.6 --parameter 2.4 --plot-curves

Example that "converges" to period 2 (bouncing between two states)

.. code-block::

   $ python chaos.main --initial 0.3 0.4 0.5 0.6 --parameter 3.1 --plot-curves

Example that "converges" to period 2 in more than 100 iterations

.. code-block::

   $ python chaos.main --initial 0.3 0.4 0.5 0.6 --parameter 3 --max-iteration 1000 --plot-curves

Example that "converges" to period 4

.. code-block::

   $ python chaos.main --initial 0.3 0.4 0.5 0.6 --parameter 3.4 --plot-curves

Example of a multi-parameter study with periods 1, 2, and 4

.. code-block::

   $ python chaos.main --initial 0.25 --parameter 2 3.1 3.5 --plot-curves

Begin exploring the bifurcation plot with an interactive matplotlib window

.. code-block::

   $ python chaos.main --initial 0.25 --parameter 0.0 0.99 1.01 1.5 2.0 2.99 3.01 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8 3.9 4.0 --plot-bifurcation

Save the image

.. code-block::

   $ time python chaos.main --initial 0.25 --parameter 0.0 0.99 1.01 1.5 2.0 2.99 3.01 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8 3.9 4.0 --plot-bifurcation bifurcation.png

   real	0m4.462s
   user	0m5.096s
   sys	0m0.146s

.. image:: bifurcation.png

More complete image that requires slightly more compute time. Better period
detection may require more calculation iterations to refine the image.

.. code-block::

   $ time python -m chaos.main --initial 0.25 --parameter 0.99 1.01 2.99 3.01 --parameter-arange 0.0 0.99 0.05 --parameter-arange 1.05 2.99 0.05 --parameter-arange 3.1 4. 0.01 --max-iteration 2000 --plot-bifurcation bifurcation_arange.png

   real	0m28.894s
   user	0m29.555s
   sys	0m0.156s

.. image:: bifurcation_arange.png

====
Test
====

.. code-block::

   $ pytest

=====
Style
=====

.. code-block::

   $ black .
