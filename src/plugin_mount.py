class PluginMount(type):
    """
    adapted from:

    http://stackoverflow.com/questions/14510286/
    plugin-architecture-plugin-manager-vs-inspecting-from-plugins-import
    """

    def __init__(cls, name, bases, attrs):
        """Called when a Plugin derived class is imported"""
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        """Add the plugin to the plugin list and perform any registration logic"""
        instance = plugin()
        cls.plugins.append(instance)
