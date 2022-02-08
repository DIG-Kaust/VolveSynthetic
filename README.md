# VolveSynthetic

![VolveSynthetic](https://github.com/DIG-Kaust/VolveSynthetic/blob/main/Figures/workflow.png)


This repository contains a set of workflows used to generate a Volve-alike synthetic dataset for 
testing of seismic processing and imaging algorithms.

**NOTE**: due to their large size, the various datasets cannot be shared directly in this repository.
If interested, contact the authors directly!

## Project structure
This repository is organized as follows:

* **Inversion**: directory containing a jupyter notebook to perform poststack inversion and save the velocity model used for modelling.
* **Modelling**: directory containing Madagascar scripts for modelling.
* **Processing**: directory containing Python notebooks for processing.
* **Imaging**: directory containing Madagascar scripts for imaging.
* **Visualization**: directory containing Python used to visualize the generated data.
* **Data**: directory containing all the datasets that we have generated in .npz and/or binary format.
* **Figures**: directory containing all figures created in the Python scripts.

A visual description of the various components is provided in the figure at the top of the README fine.

## Used software
As part of this project, we have used 2 main pieces of software:
* **Python**: used for visualization purposes as well as to create the sharp velocity model and process seismic data (i.e., up/down sepatation and deconvolution). In both cases we rely on tools provided by the PyLops framework for inverse problems.
* **Madagascar**: used for modelling and imaging. More specifically, we use a vector-acoustic (i.e., first-order staggered grid acoustic wave equation) FD modelling code for modelling, and a acoustic FD modelling code for imaging.


## Getting started
We envision two levels of users: *basic* and *advanced*.

Basic users simply want to access the data that we have already modelled, alongside the velocity model and images. Such users should head over to
the `Visualization` directory where they will be able to see how the different files created in this repository can be loaded and visualized in Python.

Advanced users are perhaps interested to create their own data using more advanced physics (e.g., elastic, attenuation, anisotropy) or look into the details
of how our velocity model and data have been created. In this case, we invite users to refer to the above figure to understand which directory contains the
required script to create our derivative work. 

