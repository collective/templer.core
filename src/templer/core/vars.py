import sys
from paste.script.templates import var as base_var


##########################################################################
# Mode constants

# keep these lowercased, as choicesvars are lowercased

EXPERT = 'expert'
EASY = 'easy'
ALL = 'all'

##########################################################################
# Variable classes

class ValidationException(ValueError):
    """Invalid value provided for variable."""


class var(base_var):

    _default_widget = 'string'

    def __init__(self, name, description,
                 default='', should_echo=True,
                 title=None, help=None, widget=None,
                 modes=(EASY, EXPERT), page='Main'):
        self.name = name
        self.description = description
        self.default = default
        self.should_echo = should_echo
        self.title = title
        self.help = help
        if not widget:
            self.widget = self._default_widget
        else:
            self.widget = widget
        self.modes = modes
        self.page = page

    def pretty_description(self):
        title = getattr(self, 'title', self.name) or self.name

        if self.description:
            return '%s (%s)' % (title, self.description)
        else:
            return title
    
    def further_help(self):
        """ return the help string for this class or inform user that none is
            available
        """
        no_help = "Sorry, no further help is available for %s\n" % self.name
        return self.help and self.help or no_help

    def validate(self, value):
        raise NotImplementedError


class BooleanVar(var):
    _default_widget = 'boolean'

    def validate(self, value):
        #Get rid of bonus whitespace
        if isinstance(value, basestring):
            value = value.strip().lower()

        #Map special cases to correct values.
        if value in ['t', 'y', 'yes', 'true', 1]: 
            value = True
        elif value in ['f','n','no', 'false', 0]:
            value = False

        if type(value) != bool:
            raise ValidationException("Not a valid boolean value: %s" % value)

        return value


class StringVar(var):
    """Single string values."""

    _default_widget = 'string'

    def validate(self, value):
        if not isinstance(value, basestring):
            raise ValidationException("Not a string value: %s" % value)

        value = value.strip()

        return value

class StringChoiceVar(var):
    """Choice of strings."""

    _default_widget = 'select'

    def __init__(self, *args, **kwargs):
        self.choices = kwargs['choices']
        del kwargs['choices']
        super(StringChoiceVar, self).__init__(*args, **kwargs)

    def validate(self, value):
        value = value.strip().lower()
        if not value in self.choices:
            raise ValidationException("Not a valid value: %s" % value)

        return value

class TextVar(StringVar):
    """Multi-line values."""

    _default_widget = 'text'


class OnOffVar(StringVar):
    """'On' or 'Off' text values."""

    _default_widget = 'onoff'

    def validate(self, value):
        #Get rid of bonus whitespace
        if isinstance(value, basestring):
            value = value.strip().lower()

        #Map special cases to correct values.
        if value in ['t', 'y', 'yes', 'true', 1, 'on']: 
            value = 'on'
        elif value in ['f','n','no', 'false', 0, 'off']:
            value = 'off'
        else:
            raise ValidationException("Not a valid on/off value: %s" % value)

        return value


class IntVar(var):
    """Integer values"""
    
    _default_widget = 'string'
    
    def validate(self, value):
        try:
            value = int(value)
        except ValueError:
            raise ValidationException("Not a valid int: %s" % value)
        
        return value
    

MAXINT = sys.maxint
MININT = -MAXINT-1
class BoundedIntVar(IntVar):
    """Integer values with allowed maximum and minimum values"""
    
    def __init__(self, *args, **kwargs):
        if 'min' in kwargs:
            self.min = kwargs.pop('min')
        else:
            self.min = MININT
        
        if 'max' in kwargs:
            self.max = kwargs.pop('max')
        else:
            self.max = MAXINT
            
        super(BoundedIntVar, self).__init__(*args, **kwargs)
    
    def validate(self, value):
        # first validate that value is an integer
        try:
            val = super(BoundedIntVar, self).validate(value)
        except ValidationException, e:
            raise e
        
        if not self.min <= val <= self.max:
            msg = "%d does not fall within allowed bounds: %d:%d"
            raise ValidationException(msg % (val, self.min, self.max))
        
        return val
    

class DottedVar(var):
    """Variable for 'dotted Python name', eg, 'foo.bar.baz'"""

    _default_widget = 'string'

    def validate(self, value):
        if not isinstance(value, basestring):
            raise ValidationException("Not a string value: %s" % value)
        value = value.strip()

        names = value.split(".")
        for name in names:
            # Check if Python identifier, http://code.activestate.com/recipes/413487/
            try:
                class test(object): __slots__ = [name]
            except TypeError:
                raise ValidationException("Not a valid Python dotted name: %s ('%s' is not an identifier)" % (value, name))

        return value

