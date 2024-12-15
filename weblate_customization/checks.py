
from weblate.checks.base import TargetCheck

class LegacyFormattingCodeCheck(TargetCheck):
    check_id = 'minecraft_legacy_formatting_code'
    name = 'Legacy Formatting Codes'
    description = 'Translation contains legacy formatting code. Apply formatting in code instead'

    def check_single(self, source, target, unit):
        return '§' not in target
