
from enum import Enum
import re
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from weblate.checks.base import TargetCheck
from weblate.checks.format import JAVA_MATCH

ALLOWED_FORMAT_SPECIFIERS = re.compile(r'%(?:(\d+)\$)?s')

class IndexingStyle(Enum):
    POSITIONAL = 0 # %s
    INDEXED = 1 # %1$s
    MIXED = 2
    NONE = 3 # no formatting codes

    @classmethod
    def get_style(cls, target):
        target = target.replace('%%', '')
        style = IndexingStyle.NONE
        for m in JAVA_MATCH.finditer(target):
            m = ALLOWED_FORMAT_SPECIFIERS.fullmatch(m.group())
            if m is None:
                continue
            is_positional = m.group(1) is None
            if is_positional:
                if style == IndexingStyle.INDEXED:
                    return IndexingStyle.MIXED
                style = IndexingStyle.POSITIONAL
            else:
                if style == IndexingStyle.POSITIONAL:
                    return IndexingStyle.MIXED
                style = IndexingStyle.INDEXED
        return style

class LegacyFormattingCodeCheck(TargetCheck):
    check_id = 'minecraft_legacy_formatting_code'
    name = 'Legacy formatting codes'
    description = 'Translation contains legacy formatting code. Apply formatting in code instead'
    default_disabled = True

    def check_single(self, source, target, unit):
        return '§' in target


class PercentSOnlyCheck(TargetCheck):
    check_id = 'percent_s_only'
    name = 'Percent S only'
    description = 'Translation contains a format specifier which is not "%s" or "%n$s"'
    default_disabled = True

    def check_single(self, source, target, unit):
        return any(PercentSOnlyCheck.get_illegal_format_codes(target))
    
    def get_description(self, check_obj):
        unit = check_obj.unit
        targets = unit.get_target_plurals()
        if len(targets) != 1:
            return super().get_description(check_obj)
        
        errors = [
            f'Translation contains illegal format specifier "{code}", use "%s" or "%n$s" only' 
            for code in set(PercentSOnlyCheck.get_illegal_format_codes(targets[0]))
        ]
        if len(errors) == 0:
            return super().get_description(check_obj)
        
        return format_html_join(mark_safe("<br />"), "{}", ((error,) for error in errors))
    
    @classmethod
    def get_illegal_format_codes(cls, target):
        for m in JAVA_MATCH.finditer(target.replace('%%', '')):
            if not ALLOWED_FORMAT_SPECIFIERS.fullmatch(m.group()):
                yield m.group()

class PercentUnescapedCheck(TargetCheck):
    check_id = 'percent_unescaped'
    name = 'Unescaped percent'
    description = 'Translation contains unescaped "%"'
    default_disabled = True

    def check_single(self, source, target, unit):
        target = target.replace('%%', '')
        for i in range(len(target)):
            if target[i] == '%' and not JAVA_MATCH.match(target, i):
                return True
        return False

class MixedIndexedFormatSpecifiersCheck(TargetCheck):
    check_id = 'mixed_indexed_format_specifiers'
    name = 'Mixed indexed format specifiers'
    description = 'Translation contains mixed indexed and positional format specifiers'
    default_disabled = True

    def check_single(self, source, target, unit):
        if any(PercentSOnlyCheck.get_illegal_format_codes(target)):
            return False # will trigger another check
        return IndexingStyle.get_style(target) == IndexingStyle.MIXED

class MismatchedFormatSpecifiersCheck(TargetCheck):
    check_id = 'mismatched_format_specifiers'
    name = 'Mismatched format specifiers'
    description = 'Translation contains mismatched format specifiers from the source'
    default_disabled = True

    def check_single(self, source, target, unit):
        return any(MismatchedFormatSpecifiersCheck.get_problems(source, target))
    
    def get_description(self, check_obj):
        unit = check_obj.unit
        sources = unit.get_source_plurals()
        targets = unit.get_target_plurals()
        if len(sources) != 1 or len(targets) != 1:
            return super().get_description(check_obj)
        
        errors = list(MismatchedFormatSpecifiersCheck.get_problems(sources[0], targets[0]))
        if len(errors) == 0:
            return super().get_description(check_obj)
        
        return format_html_join(mark_safe("<br />"), "{}", ((error,) for error in errors))

    @classmethod
    def get_problems(cls, source, target):
        source_style = IndexingStyle.get_style(source)
        target_style = IndexingStyle.get_style(target)
        if any(PercentSOnlyCheck.get_illegal_format_codes(source)) or source_style == IndexingStyle.INDEXED or source_style == IndexingStyle.MIXED:
            return # source is botched, don't report
        if any(PercentSOnlyCheck.get_illegal_format_codes(target)) or target_style == IndexingStyle.MIXED:
            return # will trigger another check
        
        source = source.replace('%%', '')
        target = target.replace('%%', '')

        num_specifiers_in_source = len(ALLOWED_FORMAT_SPECIFIERS.finditer(source))
        
        if target_style == IndexingStyle.INDEXED:
            used_indexes = set()
            reported_duplicates = set()
            for m in ALLOWED_FORMAT_SPECIFIERS.finditer(target):
                index = int(m.group(1))
                if index in used_indexes:
                    if index not in reported_duplicates:
                        yield f'Translation contains duplicate format specifier "{m.group()}"'
                        reported_duplicates.add(index)
                else:
                    used_indexes.add(index)
            for i in range(num_specifiers_in_source):
                if (i + 1) not in used_indexes:
                    yield f'Translation does not have a format specifier for index {i + 1}'
            for used_index in used_indexes:
                yield f'Translation has format specifier "%{used_index}$s" which is not present in the source'
        else:
            num_specifiers_in_target = len(ALLOWED_FORMAT_SPECIFIERS.finditer(target))
            if num_specifiers_in_target < num_specifiers_in_source:
                yield f'Translation contains {num_specifiers_in_source - num_specifiers_in_target} fewer format specifiers than the source'
            elif num_specifiers_in_target > num_specifiers_in_source:
                yield f'Translation contains {num_specifiers_in_target - num_specifiers_in_source} more format specifiers than the source'

            
