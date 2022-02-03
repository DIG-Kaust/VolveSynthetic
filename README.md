# VolveSynthetic

This repository contains a set of workflows used to generate a Volve-alike synthetic dataset for 
testing of seismic processing and imaging algorithms.


## Project structure
This repository is organized as follows:

* **Data**: directory containing all the datasets that we have generated in .npz format.
* **Inversion**: directory containing a jupyter notebook to perform poststack inversion and save the velocity model used for modelling.
* **Modelling**: directory containing Madagascar scripts for modelling.
* **Imaging**: directory containing Madagascar scripts for imaging.


A better visual understanding of how the various components are put together is provided by the following figure.


## Used software
As part of this project, we have used 2 main pieces of software:
* **Python**: used for visualization purposes as well as to create the sharp velocity model and processed seismic data. In both cases we 
rely on tools provided by the PyLops framework for inverse problems.
* **Madagascar**: used for modelling and imaging. More specifically, we use a vector-acoustic (i.e., first-order staggered grid acoustic wave equation) FD modelling code for modelling, and a acoustic FD modelling code for imaging.


## Getting started
We envision two levels of users: *basic* and *advanced*.

Basic users simply want to access the data that we have already modelled, alongside the velocity model and images. Such users should head over to
the `Visualization` directory where they will be able to see how the different files created in this repository can be loaded and visualized in Python.

Advanced users are perhaps interested to create their own data using more advanced physics (e.g., elastic, attenuation, anisotropy) or look into the details
of how our velocity model and data have been created. In this case, we invite users to refer to the above figure to understand which directory contains the
required script to create our derivative work. 

