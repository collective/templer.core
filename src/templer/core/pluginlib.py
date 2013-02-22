# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import pkg_resources


def resolve_plugins(plugin_list):
    found = []
    while plugin_list:
        plugin = plugin_list.pop()
        try:
            pkg_resources.require(plugin)
        except pkg_resources.DistributionNotFound, e:
            msg = '%sNot Found%s: %s (did you run python setup.py develop?)'
            if str(e) != plugin:
                e.args = (msg % (str(e) + ': ', ' for', plugin)),
            else:
                e.args = (msg % ('', '', plugin)),
            raise
        found.append(plugin)
        dist = get_distro(plugin)
        if dist.has_metadata('paster_plugins.txt'):
            data = dist.get_metadata('paster_plugins.txt')
            for add_plugin in parse_lines(data):
                if add_plugin not in found:
                    plugin_list.append(add_plugin)
    return map(get_distro, found)

def get_distro(spec):
    return pkg_resources.get_distribution(spec)

def load_commands_from_plugins(plugins):
    commands = {}
    for plugin in plugins:
        commands.update(pkg_resources.get_entry_map(
            plugin, group='paste.paster_command'))
    return commands

def parse_lines(data):
    result = []
    for line in data.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            result.append(line)
    return result

def egg_name(dist_name):
    return pkg_resources.to_filename(pkg_resources.safe_name(dist_name))

def egg_info_dir(base_dir, dist_name):
    all = []
    for dir_extension in ['.'] + os.listdir(base_dir):
        full = os.path.join(base_dir, dir_extension,
                            egg_name(dist_name)+'.egg-info')
        all.append(full)
        if os.path.exists(full):
            return full
    raise IOError("No egg-info directory found (looked in %s)"
                  % ', '.join(all))
