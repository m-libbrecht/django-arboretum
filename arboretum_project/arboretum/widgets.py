from itertools import chain
from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from mptt.templatetags.mptt_tags import cache_tree_children


# import json and take into account this is done differently according to the django version
try:
    import simplejson as json
except ImportError:
    import json


# Define local dictionary with Default settings
ARBORETUM_DEFAULTS = {
    'select_mode': 2,
    'checkbox': True,
    'containermode': True,
    'theme_url': None,
}

# Start with a copy of the above default settings
ARBORETUM = ARBORETUM_DEFAULTS.copy()

# Override with user settings from the project's settings.py file
ARBORETUM.update(getattr(settings, 'ARBORETUM', {}))




# Uses the Javascript dynamic tree view plugin for jQuery

# We implement the fancytree in the context of an Django mptt model,
#
# The following naming conventions are used
#
# node_model_instance : an instance of the model that represents the actual data behind the nodes of the tree


# In the HTML Document Object model, all HTML elements are element nodes, the document itself is a document node
# the Tree corresponds to HTML document corresponds to all HTML document nodes are associated with django model instances


# In order to provide the FancyTree plugin with the necessary tree node data , we will define a JavaScript variable
# fancytree_data_id_xxx that contains nested JSON data

# In order to generate the JSON data,  we will call the get_tree function
# that is defined below to recursively build up the tree data from the database to
#
# Define first 2 auxilary functions to iterate recurrently over the different tree nodes

# get_node()
#
# Gets a key pair value (dictionnary) that represents the tree node (name and associate primary key of the database table)
# In django the model is responsable from getting the data from the database, so we get this data from the corresponding model instances
#
def get_node(node_model_instance, values):
    # it is possible to customize getting the node data. To that end, a method get_node_model_instance can be defined in the model
    # if such a method has been defined in the model, call it
    if hasattr(node_model_instance, "get_data"):
        return node_model_instance.get_data(values)

    # normally the Fancytree expects 'title' as the Display name of the tree node text
    # if the models has 'name', use this instead (title is substituted)
    if hasattr(node_model_instance, "name"):
        name = node_model_instance.name
    else:
        name = unicode(node_model_instance)
    node = {"title": name, "key": node_model_instance.pk}

    if str(node_model_instance.pk) in values:
        node['select'] = True
        node['expand'] = True
    return node


def recursive_node_to_dict(node_model_instance, values, containermode):
    result = get_node(node_model_instance, values)
    children = [recursive_node_to_dict(c, values, containermode) for c in node_model_instance.get_children()]
    if children:
        expand = [c for c in children if c.get('select', False)]
        if expand:
            result["expand"] = True
        if containermode:
            result["folder"] = True
        result['children'] = children
    return result


# We will make use of the django-mptt cache_tree_chilren() function  ( in mptt.templatetags.mptt_tags  ) to call all nodes at once
# and avoid roundtrips to the database wich will slow down the process
def get_tree(node_model_instances, values, containermode):
    # get all the mptt data and cache it in root_nodes
    root_nodes = cache_tree_children(node_model_instances)
    dicts = []

    # Iterate over all nodes and
    for n in root_nodes:
        dicts.append(recursive_node_to_dict(n, values, containermode))
    return dicts


#
# DEFINE   FancyTreeWidget CLASS
#
#   Note: Fancytree API:    http://www.wwwendt.de/tech/fancytree/doc/jsdoc/
#
# Fancytree Options
# select_mode  1:single, 2:multi, 3:multi-hier (default: 2)
# checkbox  indicates if checkboxes have to be added
# containermode: If containermode = True, a distinction will be made between nodes having children
# which will be represented by a folder icon and nodes that have no children which will be represented
# by a file icon. If containermode  false, all nodes will be represented with a file icon regardless if they have
# children or not.



# This tree widget assumes the name field of the tree nodes are  ModelMultipleChoiceFields
# Since ModelMultipleChoiceField inherits from django.forms.fields.Choicefield, it has a property (field) choices
# which is a django.forms.models.ModelChoiceIterator wich has the 2 properties 'field' and 'queryset'



#   The widget accepts queryset option, which expects pre-ordered queryset by "tree_id" and "lft".




#   If you want to adjust tree data creation, you can define 'get_data' method on your model. Example:
#   def get_data(self, values):
#       doc = {"title": name, "key": self.pk}
#       if str(self.pk) in values:
#           doc['select'] = True
#           doc['expand'] = True
#       return doc



# Default settings are picked up from the ARBORETUM dictionary defined in the settings.py file

class FancyTreeWidget(forms.Widget):
    def __init__(self, attrs=None, choices=(), queryset=None, select_mode=ARBORETUM.get('select_mode'),
                 checkbox=ARBORETUM.get('checkbox'), containermode=ARBORETUM.get('containermode')):
        super(FancyTreeWidget, self).__init__(attrs)
        self.queryset = queryset
        self.select_mode = select_mode
        self.checkbox = checkbox
        self.choices = list(choices)
        self.containermode = containermode


    # override the value_from_datadict method:
    #
    # Given a dictionary of data and this widget 's name , returns the value of this widget.
    # files may contain data coming from requeqt.FILES. Returns None if a value wasn't provided.
    # Note also that value_from_datadict may be called more than once during handling of form data,
    # so if you customize it and add expensive processing, you should implement some caching mechanism yourself.
    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)


    #   override the render method of the Django Widget Base Class
    #
    #   render  Returns HTML for the widget, as a Unicode string.
    #   attrs   A dictionary containing HTML attributes to be set on the rendered widget.


    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            # make value a list
            value = []
        if not isinstance(value, (list, tuple)):
            value = [value]
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)



        # start with adding <div> tags, defining a division or a section in the HTML resder output.
        if has_id:
            output = [u'<div id="%s"></div>' % attrs['id']]
            id_attr = u' id="%s_checkboxes"' % (attrs['id'])
        else:


            output = [u'<div></div>']
            id_attr = u''
        output.append(u'<ul class="fancytree_checkboxes"%s>' % id_attr)
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], option_value))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(
                u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label)
            )
        output.append(u'</ul>')
        output.append(u'<script type="text/javascript">')

        if has_id:
            output.append(u'var fancytree_data_%s = %s;' % (
                attrs['id'],
                json.dumps(get_tree(self.queryset, str_values, self.containermode))
            ))
            output.append(
                """
                $(".fancytree_checkboxes").hide();
                $(function() {
                    $("#%(id)s").fancytree({


               extensions: ['contextMenu'],





                          contextMenu: {
				   menu: {
                'add': { 'name': 'Add                 ', 'icon': 'add' },
                'cut': { 'name': 'Cut', 'icon': 'cut' },
                'copy': { 'name': 'Copy', 'icon': 'copy' },
                'paste': { 'name': 'Paste', 'icon': 'paste' },
                'delete': { 'name': 'Delete', 'icon': 'delete', 'disabled': false },
                'deselect': { 'name': 'Unselect', 'icon': 'selectnone' },
                'selectall': { 'name': 'Select_all', 'icon': 'selectall' },
                'selectinvert': { 'name': 'Invert_Selection', 'icon': 'selectinvert' },
                'sep1': '-----------------',
                'rebuild': { 'name': 'Rebuild', 'icon': 'rebuild' },
                'help': { 'name': 'Help', 'icon': 'help' }

            },
				actions: function(node, action, options) {
					$('#selected-action').text('Selected action "' + action + '" on node ' + node);
				}
			},







                        checkbox: %(checkbox)d,
                        selectMode: %(select_mode)d,
                        source: fancytree_data_%(id)s,
                        debugLevel: %(debug)d,
                        select: function(event, data) {
                            $('#%(id)s_checkboxes').find('input[type=checkbox]').removeProp('checked');
                            var selNodes = data.tree.getSelectedNodes(%(select_mode)d === 3);
                            var selKeys = $.map(selNodes, function(node){
                                   $('#%(id)s_' + (node.key)).prop('checked', 'checked');
                                   return node.key;
                            });
                        },
                        click: function(event, data) {
                            var node = data.node;
                            if (event.targetType == "fancytreeclick")
                                node.toggleSelected();
                        },
                        keydown: function(event, data) {
                            var node = data.node;
                            if (event.which == 32) {
                                node.toggleSelected();
                                return false;
                            }
                        }
                    });
                });








                """ % {
                    'id': attrs['id'],
                    'debug': settings.DEBUG and 1 or 0,
                    'select_mode': self.select_mode,
                    'checkbox': self.checkbox,
                }
            );
        output.append(u'</script>')
        return mark_safe(u'\n'.join(output))


    # Specify the Form.Wiget's media assets: ( Django Media class )
    # Every time the Widget is used on a form, that form will be directed to include the CSS file  JavaScript files specified hereafter
    # This static definition is converted at runtime into a widget property named media.
    # The list of assets for a FancyTreeWidget instance can be retrieved through this property:
    class Media:
        css = {
            'all': (ARBORETUM.get('theme_url'),
            'contextmenu/css/jquery.contextMenu.css',
            )
        }
        js = (
            'fancytree/jquery.fancytree.min.js',
            'contextmenu/js/jquery.contextMenu-1.6.5.js',
            'contextmenu/js/jquery.fancytree.contextMenu.js',
        )
