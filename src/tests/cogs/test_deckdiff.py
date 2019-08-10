""" Testing module for src.cogs.deckdiff. """
import unittest
import urllib.error

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
        self.assertEqual(len(obj.valid_urls), 5)
        self.assertEqual(
            obj.valid_urls["deckstats.net"]["query"],
            [("export_dec", "1")],
            )
        self.assertEqual(
            obj.valid_urls["tappedout.net"]["query"],
            [("fmt", "txt")],
            )
        self.assertEqual(
            obj.valid_urls["www.mtggoldfish.com"]["paths"],
            [{"value": "download", "index": 2}],
            )
        self.assertEqual(
            obj.valid_urls["www.hareruyamtg.com"]["paths"],
            [{"value": "download", "index": 3}],
            )
        self.assertEqual(
            obj.valid_urls["www.hareruyamtg.com"]["replace"],
            [{"old": "/show/", "new": ""}],
            )
        self.assertEqual(
            obj.valid_urls["archidekt.com"]["paths"],
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
        left = {"key1": 1}
        right = {"key1": 1}
        expected_result = ([], [], [], [])

        # When
        result = Diff(self.bot).get_diff(left, right)

        # Then
        self.assertEqual(result, expected_result)

    def test_all_diff(self):
        """ Test a scenario with all cases. """
        # Given
        left = {"key1": 1, "key2": 1, "key3": 3}
        right = {"key1": 1, "key2": 4, "key3": 1}
        expected_result = ([2], ["key3"], [3], ["key2"])

        # When
        result = Diff(self.bot).get_diff(left, right)

        # Then
        self.assertEqual(result, expected_result)


class TestFormatDiffEmbed(unittest.TestCase):
    """ Tests for src.cogs.deckdiff.Diff.format_diff_embed. """

    def setUp(self):
        """ Generic variables. """
        self.bot = "a bot"

    def test_empty(self):
        """ Test when diff provided is empty. """
        # Given
        name = "title for comparison"
        diff = ([], [], [], [])
        result = Embed()  # TODO don't pass result as a variable
        expected_result = result

        # When
        Diff(self.bot).format_diff_embed(diff, name, result)

        # Then
        self.assertTrue("fields" not in result.to_dict())

    def test_format(self):
        """ Test when diff provided has data. """
        # Given
        name = "title for comparison"
        diff = ([2], ["key3"], [3], ["key2"])
        result = Embed()  # TODO don't pass result as a variable
        expected_field1 = result
        expected_field1 = result

        # When
        Diff(self.bot).format_diff_embed(diff, name, result)
        fields = result.to_dict()["fields"]

        # Then
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["inline"], True)
        self.assertEqual(fields[0]["value"], "2 key3")
        self.assertEqual(fields[1]["inline"], True)
        self.assertEqual(fields[1]["value"], "3 key2")


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
        expected_result = (defaultdict(int), defaultdict(int))

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
        expected_result = (defaultdict(int), defaultdict(int))

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
        expected_result = (defaultdict(int), {"key1": 1})

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
        expected_result = ({"key1": 1}, defaultdict(int))

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
        expected_result = ({"key1": 1}, {"key2": 2})

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
        expected_result = None

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
        url_angles = "<{url}>".format(url=url)
        expected_result = url

        # When/Then
        obj = Diff(self.bot)
        obj.valid_urls.update({"valid.com": {'bad': 'config'}})
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
        obj.valid_urls.update({"valid.com": {'bad': 'config'}})
        result = obj.get_valid_url(url)

        # Then
        self.assertEqual(result, expected_result)

    def test_query(self):
        """ Test valid URL with a query configuration. """
        # Given
        url = "http://valid.com/"
        param = "param1"
        value = "value1"

        expected_result = "{url}?{param}={value}".format(
            url=url, param=param, value=value)

        # When/Then
        obj = Diff(self.bot)
        obj.valid_urls.update(
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
        expected_result = "{url}/{path}".format(
            url=url, path=path)

        # When/Then
        obj = Diff(self.bot)
        obj.valid_urls.update(
            {"valid.com": {
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
        obj.valid_urls.update(
            {"valid.com": {
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
        data = '''
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
            }}'''.format(
                name_main=name_main,
                quantity_main=quantity_main,
                name_side=name_side,
                quantity_side=quantity_side,
                category=category,
                )
        expected_result = (
            "{quantity_main} {name_main}\n"
            "//Sideboard\n"
            "{quantity_side} {name_side}".format(
                name_main=name_main,
                quantity_main=quantity_main,
                name_side=name_side,
                quantity_side=quantity_side,
                )
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
        message = "!command {0}".format(self.url1)
        expected_result = (False, "Exactly two urls are needed.")

        url_mock.side_effect= [self.url1]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_called_once_with(self.url1)

    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_more_two_urls(self, url_mock):
        """ Test when amount of URLs provided is more than two. """
        # Given
        message = "!command {0} {0} {1}".format(self.url1, self.url2)
        expected_result = (False, "Exactly two urls are needed.")

        url_mock.side_effect= [self.url1, self.url1, self.url2]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url1),
            call(self.url2),
            ])

    @patch("src.cogs.deckdiff.urllib.request.Request")
    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_fail_open_url(self, url_mock, request_mock):
        """ Test error when URL can't be opened. """
        # Given
        message = "!command {0} {1}".format(self.url1, self.url2)
        expected_result = (False, "Failed to open url.")

        url_mock.side_effect = [self.url1, self.url2]
        request_mock.side_effect = urllib.error.URLError("Error")

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        request_mock.assert_called_once_with(
            self.url1, headers={'User-Agent': 'Mozilla/5.0'})

    @patch("src.cogs.deckdiff.Diff.get_diff")
    @patch("src.cogs.deckdiff.Diff.get_list")
    @patch("src.cogs.deckdiff.urllib.request.urlopen")
    @patch("src.cogs.deckdiff.urllib.request.Request")
    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_over_length(
            self, url_mock, request_mock, open_mock,
            list_mock, diff_mock):
        """ Test error when result is too long. """
        # Given
        message = "!command {0} {1}".format(self.url1, self.url2)
        expected_request = MagicMock()
        expected_data = "some data".encode()
        expected_lists = [MagicMock(), MagicMock()]
        over_size_diff = ([1], ["1 {0}".format("X" * 1024)], [], [])
        expected_result = (False, "Diff too long.")

        url_mock.side_effect = [self.url1, self.url2]
        request_mock.side_effect = [expected_request, None]
        open_mock.return_value.read.side_effect = [
            expected_data, "".encode()]
        list_mock.return_value = expected_lists
        diff_mock.side_effect = [over_size_diff, ([], [], [], [])]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        request_mock.assert_has_calls([
            call(self.url1, headers={'User-Agent': 'Mozilla/5.0'}),
            call(self.url2, headers={'User-Agent': 'Mozilla/5.0'}),
            ])
        open_mock.assert_has_calls([
            call(expected_request),
            call().read(),
            call(None),
            call().read(),
            ])
        list_mock.assert_has_calls([
            call(expected_data.decode("utf-8", "replace")),
            call(""),
            ])
        diff_mock.assert_has_calls([
            call(expected_lists[0], expected_lists[0]),
            call(expected_lists[1], expected_lists[1]),
            ])

    @patch("src.cogs.deckdiff.Embed")
    @patch("src.cogs.deckdiff.Diff.get_diff")
    @patch("src.cogs.deckdiff.Diff.get_list")
    @patch("src.cogs.deckdiff.urllib.request.urlopen")
    @patch("src.cogs.deckdiff.urllib.request.Request")
    @patch("src.cogs.deckdiff.Diff.get_valid_url")
    def test_success(
            self, url_mock, request_mock, open_mock,
            list_mock, diff_mock, embed_mock):
        """ Test error when result is too long. """
        # Given
        message = "!command {0} {1}".format(self.url1, self.url2)
        expected_request = MagicMock()
        expected_data = "some data".encode()
        expected_lists = [MagicMock(), MagicMock()]
        diff = (
            [1], ["{0}".format("X" * 50)],
            [3], ["{0}".format("X" * 50)],
            )
        expected_result = (True, embed_mock())

        url_mock.side_effect = [self.url1, self.url2]
        request_mock.side_effect = [expected_request, None]
        open_mock.return_value.read.side_effect = [
            expected_data, "".encode()]
        list_mock.return_value = expected_lists
        diff_mock.side_effect = [diff, ([], [], [], [])]

        # When
        result = Diff(self.bot).execute(message)

        # Then
        self.assertEqual(result, expected_result)
        url_mock.assert_has_calls([
            call(self.url1),
            call(self.url2),
            ])
        request_mock.assert_has_calls([
            call(self.url1, headers={'User-Agent': 'Mozilla/5.0'}),
            call(self.url2, headers={'User-Agent': 'Mozilla/5.0'}),
            ])
        open_mock.assert_has_calls([
            call(expected_request),
            call().read(),
            call(None),
            call().read(),
            ])
        list_mock.assert_has_calls([
            call(expected_data.decode("utf-8", "replace")),
            call(""),
            ])
        diff_mock.assert_has_calls([
            call(expected_lists[0], expected_lists[0]),
            call(expected_lists[1], expected_lists[1]),
            ])
        embed_mock.assert_has_calls([
            call(),
            call(),
            ])
