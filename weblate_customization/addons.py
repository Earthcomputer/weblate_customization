
from json import JSONEncoder
import re

from weblate.addons.json import JSONCustomizeAddon
from weblate_customization.forms import JSONCustomizeFormExt

def try_compile(regex):
    try:
        return re.compile(regex)
    except re.error:
        return re.compile('.*')

class JSONCustomizeAddonExt(JSONCustomizeAddon):
    name = 'net.earthcomputer.json.customize'
    verbose = 'Customize JSON output (extended)'
    description = 'Allows customizing JSON output more than the default JSON customization add-on, for example by adding groups of keys'
    settings_form = JSONCustomizeFormExt
    compat = {
        'file_format': {
            'json'
        }
    }

    def store_post_load(self, translation, store):
        super().store_post_load(translation, store)
        config = self.instance.configuration

        style = config.get('style', 'spaces')
        indent = int(config.get('indent', 4))
        if style == 'spaces':
            indent = ' ' * indent
        else:
            indent = '\t' * indent

        sort_keys = bool(int(config.get('sort_keys', 0)))

        groups = config.get('groups', '.*')
        groups = [try_compile(group.strip()) for group in groups.split(';')]

        class CustomJSONEncoder(JSONEncoder):
            def encode(self, obj):
                if isinstance(obj, dict) and all((isinstance(x, str) for x in obj)) and all((isinstance(x, str) for x in obj.values())):
                    kv = list(obj.items())
                    if sort_keys:
                        kv.sort()

                    result = '{'
                    for i in range(len(kv)):
                        if i != 0:
                            result += ','
                            group_num = None
                            for gn, group in enumerate(groups):
                                if group.fullmatch(kv[i][0]):
                                    group_num = gn
                                    break
                            if group_num is not None:
                                if not group.fullmatch(kv[i - 1][0]):
                                    result += '\n'
                        result += '\n' + indent
                        result += super().encode(kv[i][0]) + ': ' + super().encode(kv[i][1])
                    result += '\n}'

                    return result
                else:
                    return super().encode(obj)
        store.store.dump_args['cls'] = CustomJSONEncoder
        

