import stringprep
import unicodedata


class SASLprep:
    @staticmethod
    def saslprep(text: str):
        if SASLprep.__check_bidirectional_string(text):
            raise Exception('Bidirectional strings')
        return ''.join(list(map(SASLprep.__apply_saslgrep_profile, text)))

    @staticmethod
    def __apply_saslgrep_profile(char: str):
        # Unicode normalization form KC
        char = stringprep.map_table_b2(char)
        if SASLprep.__is_non_ascii_space_character(char):
            return ' '
        elif SASLprep.__is_commonly_mapped_to_nothing_character(char):
            return ''
        elif SASLprep.__is_prohibited_in_saslgrep(char):
            raise Exception('Prohibited character was found')
        elif SASLprep.__is_unassigned_code_point(char):
            raise Exception('Unassigned Code Points')
        return char

    @staticmethod
    def __is_prohibited_in_saslgrep(char: str):
        if stringprep.in_table_c12(char):
            # Non-ASCII space characters
            return True
        elif stringprep.in_table_c12(char):
            # ASCII control characters
            return True
        elif stringprep.in_table_c21(char):
            # Non-ASCII control characters
            return True
        elif stringprep.in_table_c22(char):
            # Private Use characters
            return True
        elif stringprep.in_table_c3(char):
            # Non-character code points
            return True
        elif stringprep.in_table_c4(char):
            # Non-character code points
            return True
        elif stringprep.in_table_c5(char):
            # Surrogate code points
            return True
        elif stringprep.in_table_c6(char):
            # Inappropriate for plain text characters
            return True
        elif stringprep.in_table_c7(char):
            # Inappropriate for canonical representation characters
            return True
        elif stringprep.in_table_c8(char):
            # Change display properties or deprecated characters
            return True
        elif stringprep.in_table_c9(char):
            # Tagging characters
            return True
        return False

    @staticmethod
    def __is_non_ascii_space_character(char: str):
        return stringprep.in_table_c12(char)

    @staticmethod
    def __is_commonly_mapped_to_nothing_character(char: str):
        return stringprep.in_table_b1(char)

    @staticmethod
    def __is_unassigned_code_point(char: str):
        return stringprep.in_table_a1(char)

    @staticmethod
    def __check_bidirectional_string(text: str):
        isContainLTR = any(
            [unicodedata.bidirectional(char) == 'L' for char in text])
        isContainRTL = any(
            [unicodedata.bidirectional(char) == 'R' for char in text])
        isContainRTLArabic = any(
            [unicodedata.bidirectional(char) == 'AL' for char in text])
        return isContainLTR + isContainRTL + isContainRTLArabic > 1
