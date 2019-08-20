""" Testing module for src.cogs.deckdiff. """
import requests
import unittest

from collections import defaultdict

from mock import (
    call,
    MagicMock,
    patch,
    )

from discord import Embed

from src.cogs.deckdiff import Diff


class TestDiffClass(unittest.TestCase):
    """ Non method specific tests for src.cogs.deckdiff.Diff. """
    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    @patch("src.cogs.deckdiff.re.compile")
    def test_init(self, re_mock):
        """ Test initial attributes. """
        # Given
        expected_angle_exp = "angle regexp"
        expected_line_exp = "line regexp"

        re_mock.side_effect = [
            expected_angle_exp,
            expected_line_exp,
            ]

        # When
        obj = Diff(self.bot)

        # Then
        self.assertEqual(obj.bot, self.bot)
        self.assertEqual(len(obj.urls_options), 5)
        self.assertEqual(
            obj.urls_options["deckstats.net"]["query"],
            [("export_dec", "1")],
            )
        self.assertEqual(
            obj.urls_options["tappedout.net"]["query"],
            [("fmt", "txt")],
            )
        self.assertEqual(
            obj.urls_options["www.mtggoldfish.com"]["paths"],
            [{"value": "download", "index": 2}],
            )
        self.assertEqual(
            obj.urls_options["www.hareruyamtg.com"]["paths"],
            [{"value": "download", "index": 3}],
            )
        self.assertEqual(
            obj.urls_options["www.hareruyamtg.com"]["replace"],
            [{"old": "/show/", "new": ""}],
            )
        self.assertEqual(
            obj.urls_options["archidekt.com"]["paths"],
            [
                {"value": "api", "index": 1},
                {"value": "small/", "index": 4},
            ],
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
    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    def test_no_diff(self):
        """ Test when data provided has no difference. """
        # Given
        left = {"key1": 1, "key2": 1, "key3": 1}
        right = {"key1": 1, "key2": 1, "key3": 1}
        expected_result = defaultdict(str)

        # When
        result = Diff(self.bot).get_diff(left, right)

        # Then
        self.assertEqual(result, expected_result)

    def test_all_diff(self):
        """ Test a scenario with all cases. """
        # Given
        left = {"key1": 1, "key2": 1, "key3": 3, "key4": 1}
        right = {"key1": 1, "key2": 4, "key3": 1, "key5": 1}
        expected_result = {
            1: "2 key3\n1 key4\n",
            2: "3 key2\n1 key5\n",
            }

        # When
        result = Diff(self.bot).get_diff(left, right)

        # Then
        self.assertEqual(result[1], expected_result[1])
        self.assertEqual(result[2], expected_result[2])


class TestFilterName(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.filter_name. """

    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    def test_no_replacement(self):
        """ Test when name is not replaced. """
        # Given
        name = "ccc"
        expected_result = name

        # When
        diff_obj = Diff(self.bot)
        diff_obj.name_replacements = {"aaa": "bbb"}
        result = diff_obj.filter_name(name)

        # Then
        self.assertEqual(result, expected_result)

    def test_replacement(self):
        """ Test when name is replaced. """
        # Given
        name = "aaa"
        expected_result = "bbb"

        # When
        diff_obj = Diff(self.bot)
        diff_obj.name_replacements = {"aaa": expected_result}
        result = diff_obj.filter_name(name)

        # Then
        self.assertEqual(result, expected_result)


class TestGetList(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.get_list. """

    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    @patch("src.cogs.deckdiff.Diff.format_to_txt")
    def test_empty(self, format_mock):
        """ Test when no data available. """
        # Given
        data = ""
        expected_result = {
            "mainboard": defaultdict(int),
            "sideboard": defaultdict(int),
            }

        format_mock.return_value = data

        # When
        result = Diff(self.bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)
        format_mock.assert_called_once_with(data)

    @patch("src.cogs.deckdiff.Diff.format_to_txt")
    def test_skip_all(self, format_mock):
        """ Test when no data matches regexp. """
        # Given
        data = "\n\n\n\n\n\n"
        expected_result = {
            "mainboard": defaultdict(int),
            "sideboard": defaultdict(int),
            }

        format_mock.return_value = data

        # When
        result = Diff(self.bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)
        format_mock.assert_called_once_with(data)

    @patch("src.cogs.deckdiff.Diff.format_to_txt")
    def test_only_sideboard(self, format_mock):
        """ Test when data has only sideboard information. """
        # Given
        data = "\n//Sideboard:\n\nSB: 1 key1\n\n"
        expected_result = {
            "mainboard": defaultdict(int),
            "sideboard": {"key1": 1},
            }

        format_mock.return_value = data

        # When
        result = Diff(self.bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)
        format_mock.assert_called_once_with(data)

    @patch("src.cogs.deckdiff.Diff.format_to_txt")
    def test_only_mainboard(self, format_mock):
        """ Test when data has only mainboard information. """
        # Given
        data = "\n\n1 key1\n\n"
        expected_result = {
            "mainboard": {"key1": 1},
            "sideboard": defaultdict(int),
            }

        format_mock.return_value = data

        # When
        result = Diff(self.bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)
        format_mock.assert_called_once_with(data)

    @patch("src.cogs.deckdiff.Diff.format_to_txt")
    def test_mainboard_sideboard(self, format_mock):
        """ Test when data has both mainboard and sideboard information. """
        # Given
        data = "\n\n1 key1\n\n//Sideboard:\n\nSB: 2 key2"
        expected_result = {
            "mainboard": {"key1": 1},
            "sideboard": {"key2": 2},
            }

        format_mock.return_value = data

        # When
        result = Diff(self.bot).get_list(data)

        # Then
        self.assertEqual(result, expected_result)
        format_mock.assert_called_once_with(data)


class TestGetValidUrl(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.get_valid_url. """

    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    def test_empty(self):
        """ Test when no data provided. """
        # Given
        url = ""
        expected_result = ""

        # When
        result = Diff(self.bot).get_valid_url(url)

        # Then
        self.assertEqual(result, expected_result)

    def test_invalid_url(self):
        """ Test error when invalid URL is provided. """
        # Given
        url = "http://invalid.com/"

        # When/Then
        with self.assertRaises(Diff.MessageError):
            Diff(self.bot).get_valid_url(url)

    def test_strip_angles(self):
        """ Test valid URL between angles (<>). """
        # Given
        url = "http://valid.com/"
        url_angles = f"<{url}>"
        expected_result = url

        # When/Then
        obj = Diff(self.bot)
        obj.urls_options.update({"valid.com": {'bad': 'config'}})
        result = obj.get_valid_url(url_angles)

        # Then
        self.assertEqual(result, expected_result)

    def test_no_configuration(self):
        """ Test valid URL but no configuration. """
        # Given
        url = "http://valid.com/"
        expected_result = url

        # When/Then
        obj = Diff(self.bot)
        obj.urls_options.update({"valid.com": {'bad': 'config'}})
        result = obj.get_valid_url(url)

        # Then
        self.assertEqual(result, expected_result)

    def test_query(self):
        """ Test valid URL with a query configuration. """
        # Given
        url = "http://valid.com/"
        param = "param1"
        value = "value1"
        expected_result = f"{url}?{param}={value}"

        # When/Then
        obj = Diff(self.bot)
        obj.urls_options.update(
            {"valid.com": {'query': [(param, value)]}})
        result = obj.get_valid_url(url)

        # Then
        self.assertEqual(result, expected_result)

    def test_path(self):
        """ Test valid URL when adding path to end of URL. """
        # Given
        url = "http://valid.com/p1/p2"
        path = "p3"
        index = 3
        expected_result = f"{url}/{path}"

        # When/Then
        obj = Diff(self.bot)
        obj.urls_options.update({
            "valid.com": {
                'paths': [{"value": path, "index": index}]}
                })
        result = obj.get_valid_url(url)

        # Then
        self.assertEqual(result, expected_result)

    def test_replace(self):
        """ Test valid URL when replacing parts of the URL. """
        # Given
        url = "http://valid.com/p1/p2"
        old = "/p2"
        new = ""
        expected_result = "http://valid.com/p1"

        # When/Then
        obj = Diff(self.bot)
        obj.urls_options.update({
            "valid.com": {
                'replace': [{"old": old, "new": new}]}
                })
        result = obj.get_valid_url(url)

        # Then
        self.assertEqual(result, expected_result)


class TestFormatToTxt(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.format_to_txt. """

    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    def test_not_json(self):
        """ Test when data provided is not valid JSON. """
        # Given
        data = "some text"
        expected_result = data

        # When
        result = Diff(self.bot).format_to_txt(data)

        # Then
        self.assertEqual(result, expected_result)

    def test_json_archidekt(self):
        """ Test when data provided is valid JSON (for archidekt). """
        # Given
        name_main = "card1"
        quantity_main = 2
        name_side = "card2"
        quantity_side = 1
        category = "Sideboard"
        data = f'''
            {{"cards":
                [
                    {{
                        "card": {{
                            "oracleCard": {{
                                "name": "{name_main}"
                                }}
                            }},
                        "quantity": "{quantity_main}",
                        "category": ""
                    }},
                    {{
                        "card": {{
                            "oracleCard": {{
                                "name": "{name_side}"
                                }}
                            }},
                        "quantity": "{quantity_side}",
                        "category": "{category}"
                    }}
                ]
            }}'''
        expected_result = (
            f"{quantity_main} {name_main}\n"
            f"//Sideboard\n"
            f"{quantity_side} {name_side}"
            )

        # When
        result = Diff(self.bot).format_to_txt(data)

        # Then
        self.assertEqual(result, expected_result)


class TestDiffExecute(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.execute. """

    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"
        self.url1 = "url1.com"
        self.url2 = "url2.com"

    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_less_two_urls(self, url_mock):
        """ Test when amount of URLs provided is less than two. """
        # Given
        message = f"!command {self.url1}"
        expected_result = (False, "Exactly two urls are needed.")

        url_mock.side_effect = [self.url1]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_called_once_with(self.url1)

    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_more_two_urls(self, url_mock):
        """ Test when amount of URLs provided is more than two. """
        # Given
        message = f"!command {self.url1} {self.url1} {self.url2}"
        expected_result = (False, "Exactly two urls are needed.")

        url_mock.side_effect = [self.url1, self.url1, self.url2]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url1),
            call(self.url2),
            ])

    @patch("src.cogs.deckdiff.requests.get")
    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_fail_open_url(self, url_mock, request_mock):
        """ Test error when URL can't be opened. """
        # Given
        message = f"!command {self.url1} {self.url2}"
        expected_result = (False, "Failed to open url.")

        url_mock.side_effect = [self.url1, self.url2]
        request_mock.side_effect = requests.exceptions.RequestException("Err")

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        request_mock.assert_called_once_with(self.url1)

    @patch("src.cogs.deckdiff.Diff.get_diff")
    @patch("src.cogs.deckdiff.Diff.get_list")
    @patch("src.cogs.deckdiff.requests.get")
    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_over_length(
            self, url_mock, request_mock, list_mock, diff_mock):
        """ Test error when result is too long. """
        # Given
        message = f"!command {self.url1} {self.url2}"
        expected_request1 = MagicMock(url="some text")
        expected_request2 = MagicMock(url="some text")
        expected_lists = [
            {
                "mainboard": MagicMock(),
                "sideboard": MagicMock(),
            },
            {
                "mainboard": "",
                "sideboard": "",
            },
            ]
        over_size_diff = {1: "X" * 1024, 2: ""}
        expected_result = (False, "Diff too long.")

        url_mock.side_effect = [self.url1, self.url2]
        request_mock.side_effect = [
            expected_request1,
            expected_request2,
            ]
        list_mock.side_effect = expected_lists
        diff_mock.side_effect = [over_size_diff, defaultdict(str)]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        request_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        list_mock.assert_has_calls([
            call(expected_request1.text),
            call(expected_request2.text),
            ])
        diff_mock.assert_has_calls([
            call(expected_lists[0]["mainboard"], expected_lists[1]["mainboard"]),
            call(expected_lists[0]["sideboard"], expected_lists[1]["sideboard"]),
            ])

    @patch("src.cogs.deckdiff.Embed")
    @patch("src.cogs.deckdiff.Diff.get_diff")
    @patch("src.cogs.deckdiff.Diff.get_list")
    @patch("src.cogs.deckdiff.requests.get")
    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_success(
            self, url_mock, request_mock, list_mock, diff_mock, embed_mock):
        """ Test error when result is too long. """
        # Given
        message = f"!command {self.url1} {self.url2}"
        expected_request1 = MagicMock(url="some text")
        expected_request2 = MagicMock(url="some text")
        expected_lists = [
            {
                "mainboard": MagicMock(),
                "sideboard": MagicMock(),
            },
            {
                "mainboard": "",
                "sideboard": "",
            },
            ]
        diff = {1: "X" * 50, 2: "X" * 50}
        expected_result = (True, embed_mock())

        url_mock.side_effect = [self.url1, self.url2]
        request_mock.side_effect = [
            expected_request1,
            expected_request2,
            ]
        list_mock.side_effect = expected_lists
        diff_mock.side_effect = [diff, defaultdict(str)]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        request_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        list_mock.assert_has_calls([
            call(expected_request1.text),
            call(expected_request2.text),
            ])
        diff_mock.assert_has_calls([
            call(expected_lists[0]["mainboard"], expected_lists[1]["mainboard"]),
            call(expected_lists[0]["sideboard"], expected_lists[1]["sideboard"]),
            ])
        embed_mock.assert_has_calls([
            call(),
            call(),
            ])
