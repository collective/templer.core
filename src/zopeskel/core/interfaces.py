class IVar:
    """Variables in a ZopeSkel template.
    """

    # actual variable name, eg "description"
    name = ""    

    # human-facing variable name, eg "Product Description"
    title = ""     
    
    # Short, 1-sentence description
    # e.g., "Short description of this product."
    description = ""

    # Longer, potentially multi-paragraph help for users
    # to explain this option
    #
    # e.g., "Products in Plone have a description that is used for ..."
    help = ""

    # Default value
    default = None

    # Should Echo   # wtf? is this used?
    should_echo = True

    # Modes that question should appear in
    # 'easy', 'intermediate', 'advanced'
    modes = ()

    # Widget hint?
    # XXX Todo
    # strawman: ('text','multitext','tf','int')

    def full_description():
        """Returns variable name and description."""

    def print_vars():
        """ wtf? """

    def validate(value):
        """Check validity of entered value; exception on error.

        Check validity of entered data and raise exception if
        value is invalid.

        If this value is valid, this method will return a
        normalized version of it (eg, "yes" -> True, for boolean
        questions).
        """





