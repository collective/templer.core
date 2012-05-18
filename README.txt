.. contents::

Introduction
============

This package provides the core functionality of the templer code generation
system. Included are a base template class, utility scripts, the templer
command-line wrapper and basic templates for basic python namespace packages and
nested namespace packages.

All functionality of the templer system is inherited from and extends 
PasteScript_ templates.  Templates can be generated using the syntax of that
package, but the templer system provides a wrapper script to make it easier
for developers to generate packages.

.. _PasteScript: http://pythonpaste.org/script/

templer script
--------------

This package provides a script, ``templer``. The script acts as a wrapper for
PasteScript's ``paster create``, hiding the newbie-error-prone syntax of that
command. The ``templer`` script also provides some inline error-checking for
project names and other variables as well as additional help. It is recommended
to use this script--especially for new users--rather than using ``paster
create`` directly. (The resulting packages produced, however, will be the same).

For example, to create a new basic namespace package invoke the script like so::

    templer basic_namespace 

This will prompt you to provide a name for your package.  The name you provide 
will be validated to ensure that it fits with the number of namespaces expected 
by the template you have chosen.

Once you have set the name for your new package, You will be asked to choose a 
set of questions to answer.  By default, only the 'easy' questions are selected, 
allowing you to create a new package with a minimum of interaction.  However, 
you may choose the ``expert`` set, or even choose to answer ``all`` questions 
if you need more control over the final output of your package.

At any time in the question-and-answer process, you may type a ``?`` at the 
prompt to recieve in-line assistance with the current question.

If you wish to quit the process at any time during the questions, simply enter
``q`` at the prompt.

Additional Script Functions
---------------------------

In addition to interactively generating code, the templer script provides a 
number of other useful functions:

    ``templer --help``
      provides full listings of the help text for the templer script.

    ``templer --list``
      provides a detailed list of the available templates
    
    ``templer --version``
      provides the version number of the currently installed templer package

Testing
=======

This package provides both unit tests for code functions and doctests for each 
of the provided templates.  If you make changes to the package, you must ensure 
that these tests run successfully before checking them in.  Please also 
contribute tests for any code you create.  To run the tests, execute the 
following::

    $ python setup.py test

