
import re
from weblate.checks.base import TargetCheck
from weblate.checks.format import JAVA_MATCH

ALLOWED_FORMATTING_CODES = re.compile(r'%(\d+\$)?s')

class LegacyFormattingCodeCheck(TargetCheck):
    check_id = 'minecraft_legacy_formatting_code'
    name = 'Legacy formatting codes'
    description = 'Translation contains legacy formatting code. Apply formatting in code instead'
    default_disabled = True

    def check_single(self, source, target, unit):
        return '§' not in target


class PercentSOnlyCheck(TargetCheck):
    check_id = 'percent_s_only'
    name = 'Percent S only'
    description = 'Translation contains a formatting code which is not "%s" or "%n$s"'
    default_disabled = True

    def check_single(self, source, target, unit):
        return not all((ALLOWED_FORMATTING_CODES.fullmatch(x.group()) for x in JAVA_MATCH.finditer(target.replace('%%', ''))))

class UnescapedPercentCheck(TargetCheck):
    check_id = 'unescaped_percent'
    name = 'Unescaped percent'
    description = 'Translation contains unescaped "%"'
    default_disabled = True

    def check_single(self, source, target, unit):
        target = target.replace('%%', '')
        for i in range(len(target)):
            if target[i] == '%' and not JAVA_MATCH.match(target, i):
                return False
        return True

class MixedIndexedFormatSpecifiersCheck(TargetCheck):
    check_id = 'mixed_indexed_format_specifiers'
    name = 'Mixed indexed format specifiers'
    description = 'Translation contains mixed indexed and positional format specifiers'
    default_disabled = True

    def check_single(self, source, target, unit):
        target = target.replace('%%', '')
        allow_positional = True
        allow_indexed = True
        for m in JAVA_MATCH.finditer(target):
            m = ALLOWED_FORMATTING_CODES.fullmatch(m.group())
            if m is None:
                return True # disallowed formatting code will trigger another check
            is_positional = m.group(1) is None
            if is_positional:
                if not allow_positional:
                    return False
                allow_indexed = False
            else:
                if not allow_indexed:
                    return False
                allow_positional = False
        return True
