""" Testing module for src.cogs.deckdiff. """
import unittest

from collections import defaultdict

from mock import (
    call,
    patch,
    )

from discord import Embed

from src.cogs.deckdiff import Diff


class TestDiff(unittest.TestCase):
    """ Non method specific tests for src.cogs.deckdiff.Diff. """

    @patch("src.cogs.deckdiff.re.compile")
    def test_init(self, re_mock):
        """ Test initial attributes. """
        # Given
        bot = "a bot"
        expected_angle_exp = "angle regexp"
        expected_line_exp = "line regexp"

        re_mock.side_effect = [
            expected_angle_exp,
            expected_line_exp,
            ]

        # When
        obj = Diff(bot)

        # Then
        self.assertEqual(obj.bot, bot)
        self.assertEqual(len(obj.valid_urls), 2)
        self.assertEqual(
            obj.valid_urls["deckstats.net"]["query"],
            [("export_dec", "1")],
            )
        self.assertEqual(
            obj.valid_urls["tappedout.net"]["query"],
            [("fmt", "txt")],
            )
        self.assertEqual(obj.re_stripangle, expected_angle_exp)
        self.assertEqual(obj.re_line, expected_line_exp)
        self.assertEqual(len(obj.name_replacements), 1)
        re_mock.assert_has_calls([
            call(r"^<(.*)>$"),
            call(
                r"^\s*(?:(?P<sb>SB:)\s)?\s*"
                r"(?P<count>[0-9]+)x?\s+(?P<name>.*?)\s*"
                r"(?:<[^>]*>\s*)*(?:#.*)?$"),
            ])

    def test_message_error(self):
        """ Test MessageError sub class. """
        # Given
        expected_message = "error message"

        # When
        result = Diff.MessageError(expected_message)

        # Then
        self.assertEqual(result.message, expected_message)
        expected_skip_exp = "skip regexp"


class TestGetDiff(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.get_diff. """

    def test_no_diff(self):
        """ Test when data provided has no difference. """
        # Given
        bot = "a bot"
        left = {"key1": 1}
        right = {"key1": 1}
        expected_result = ([], [], [], [])

        # When
        result = Diff(bot).get_diff(left, right)

        # Then
        self.assertEqual(result, expected_result)

    def test_all_diff(self):
        """ Test a scenario with all cases. """
        # Given
        bot = "a bot"
        left = {"key1": 1, "key2": 1, "key3": 3}
        right = {"key1": 1, "key2": 4, "key3": 1}
        expected_result = ([2], ["key3"], [3], ["key2"])

        # When
        result = Diff(bot).get_diff(left, right)

        # Then
        self.assertEqual(result, expected_result)


class TestFormatDiffEmbed(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.format_diff_embed. """

    def test_empty(self):
        """ Test when diff provided is empty. """
        # Given
        bot = "a bot"
        name = "title for comparison"
        diff = ([], [], [], [])
        result = Embed()  # TODO don't pass result as a variable
        expected_result = result

        # When
        Diff(bot).format_diff_embed(diff, name, result)

        # Then
        self.assertTrue("fields" not in result.to_dict())

    def test_format(self):
        """ Test when diff provided has data. """
        # Given
        bot = "a bot"
        name = "title for comparison"
        diff = ([2], ["key3"], [3], ["key2"])
        result = Embed()  # TODO don't pass result as a variable
        expected_field1 = result
        expected_field1 = result

        # When
        Diff(bot).format_diff_embed(diff, name, result)
        fields = result.to_dict()["fields"]

        # Then
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["inline"], True)
        self.assertEqual(fields[0]["value"], "2 key3")
        self.assertEqual(fields[1]["inline"], True)
        self.assertEqual(fields[1]["value"], "3 key2")


class TestFilterName(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.filter_name. """

    def test_no_replacement(self):
        """ Test when name is not replaced. """
        # Given
        bot = "a bot"
        name = "ccc"
        expected_result = name

        # When
        diff_obj = Diff(bot)
        diff_obj.name_replacements = {"aaa": "bbb"}
        result = diff_obj.filter_name(name)

        # Then
        self.assertEqual(result, expected_result)

    def test_replacement(self):
        """ Test when name is replaced. """
        # Given
        bot = "a bot"
        name = "aaa"
        expected_result = "bbb"

        # When
        diff_obj = Diff(bot)
        diff_obj.name_replacements = {"aaa": expected_result}
        result = diff_obj.filter_name(name)

        # Then
        self.assertEqual(result, expected_result)


class TestGetList(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.get_list. """

    def test_empty(self):
        """ Test when no data available. """
        # Given
        bot = "a bot"
        data = ""
        expected_result = (defaultdict(int), defaultdict(int))

        # When
        result = Diff(bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)

    def test_skip_all(self):
        """ Test when no data matches regexp. """
        # Given
        bot = "a bot"
        data = "\n\n\n\n\n\n"
        expected_result = (defaultdict(int), defaultdict(int))

        # When
        result = Diff(bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)

    def test_only_sideboard(self):
        """ Test when data has only sideboard information. """
        # Given
        bot = "a bot"
        data = "\n//Sideboard:\n\nSB: 1 key1\n\n"
        expected_result = (defaultdict(int), {"key1": 1})

        # When
        result = Diff(bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)

    def test_only_mainboard(self):
        """ Test when data has only mainboard information. """
        # Given
        bot = "a bot"
        data = "\n\n1 key1\n\n"
        expected_result = ({"key1": 1}, defaultdict(int))

        # When
        result = Diff(bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)

    def test_mainboard_sideboard(self):
        """ Test when data has both mainboard and sideboard information. """
        # Given
        bot = "a bot"
        data = "\n\n1 key1\n\n//Sideboard:\n\nSB: 2 key2"
        expected_result = ({"key1": 1}, {"key2": 2})

        # When
        result = Diff(bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)
