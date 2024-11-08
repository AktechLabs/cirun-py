Cirun's Python Client documentation!
====================================

Welcome to the official documentation for **Cirun's Python Client**. This client library allows
you to seamlessly interact with Cirun's API, enabling efficient management of repositories,
access controls, cloud integrations, and more directly from your Python applications.

.. raw:: html

    <p align="center">
        <a href="https://anaconda.org/conda-forge/cirun">
            <img src="https://img.shields.io/conda/dn/conda-forge/cirun.svg" alt="Conda Downloads">
        </a>
        <a href="https://pypi.org/project/cirun">
            <img src="https://img.shields.io/pypi/v/cirun.svg" alt="PyPI Version">
        </a>
        <a href="https://pypi.org/project/cirun">
            <img src="https://img.shields.io/pypi/pyversions/cirun.svg" alt="PyPI Python Version">
        </a>
        <a href="https://anaconda.org/conda-forge/cirun">
            <img src="https://img.shields.io/badge/recipe-cirun-green.svg" alt="Conda Recipe">
        </a>
    </p>

+--------------------+--------------------+
| |pic1| |pic2|      | |pic3|             |
+--------------------+--------------------+

.. |pic1| image:: _static/cirun-logo-light.png
   :class: only-light
   :width: 200
   :alt: cirun logo

.. |pic2| image:: _static/cirun-logo-dark.jpg
   :class: only-dark
   :width: 200
   :alt: cirun logo

.. |pic3| image:: https://cirun.io/static/media/nvidia-inception-program-badge-rgb-for-screen.2f33635d.svg
   :width: 200
   :alt: nvidia inception program logo

Installation
============

.. code-block:: bash

    pip install cirun


or via `conda-forge`

.. code-block:: bash

    conda install -c conda-forge cirun


.. toctree::
   :maxdepth: 2

   api

Features
========

Cirun's Python Client offers a following set of features to help you manage cirun integration with
your GitHub Organization:

- **Repository Management**: Connect, activate, and deactivate repositories integrated with Cirun.
- **Access Control**: Define and update access permissions for repositories, including teams, roles, and users.
- **Cloud Integrations**: Connect and manage various cloud providers directly through the client.
- **GitHub App Installation**: Simplify the installation of Cirun's GitHub App on your repositories.

Contributing
============

There are multiple ways you can contribute to cirun client

- **Add Missing Documentation**: Help improve the clarity and comprehensiveness of our docs.
- **Report Bugs**: If you encounter any issues, please report them.
- **Feature Requests**: Suggest new features or improvements.
- **Submit Pull Requests**: Implement bug fixes or new features and submit your code for review.

.. toctree::
   :hidden:
   :caption: Meta

    PyPI <https://pypi.org/project/cirun/>
    GitHub <https://github.com/aktechlabs/cirun-py/>
    Cirun <https://cirun.io>
    Cirun Docs <https://docs.cirun.io>
    X <https://x.com/CirunHQ>
