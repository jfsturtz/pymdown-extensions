"""Utilities."""
import yaml
from collections import OrderedDict
import sys
import os
import unittest
import textwrap
import markdown
import difflib

PY2 = sys.version_info >= (2, 0) and sys.version_info < (3, 0)
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)

if PY2:
    unicode_type = unicode  # noqa
    string_type = basestring  # noqa
    binary_type = str
else:
    unicode_type = str  # noqa
    string_type = str  # noqa
    binary_type = bytes  # noqa


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


class MdCase(unittest.TestCase):
    """Markdown unittest test case base."""

    extension = []
    extension_configs = {}
    base = CURRENT_DIR

    def setUp(self):
        """Setup."""

        for k1, v1 in self.extension_configs.items():
            if v1 is not None:
                for k2, v2 in v1.items():
                    if isinstance(v2, string_type):
                        v1[k2] = v2.replace(
                            '{{BASE}}', self.base
                        ).replace(
                            '{{RELATIVE}}', CURRENT_DIR
                        )
            self.extension_configs[k1] = v1

        self.md = markdown.Markdown(extensions=self.extension, extension_configs=self.extension_configs)

    def dedent(self, text, strip=False):
        """Reduce indentation."""

        return textwrap.dedent(text).strip('\n') if strip else textwrap.dedent(text)

    def check_markdown(self, text, expected, dedent=False):
        """Check the markdown."""

        if dedent:
            # For markdown, begining and ending new lines get stripped out with
            # no issues, but for HTML (expected), we need to trim.
            # If there are tests that are newline sensitive, it may make sense
            # to call dedent directly to control this.
            text = self.dedent(text)
            expected = self.dedent(expected, True)

        results = self.md.convert(text)

        diff = [
            l for l in difflib.unified_diff(
                expected.splitlines(True),
                results.splitlines(True),
                'Expected',
                'Actual',
                n=3
            )
        ]

        print(''.join(diff))
        self.assertTrue(not diff)


def yaml_load(stream, loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Custom YAML loader.

    Make all YAML dictionaries load as ordered Dicts.
    http://stackoverflow.com/a/21912744/3609487

    Load all strings as unicode.
    http://stackoverflow.com/a/2967461/3609487
    """

    def construct_mapping(loader, node):
        """Convert to ordered dict."""

        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    def construct_yaml_str(self, node):
        """Override the default string handling function to always return unicode objects."""

        return self.construct_scalar(node)

    class Loader(loader):
        """Custom Loader."""

    Loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping
    )

    Loader.add_constructor(
        'tag:yaml.org,2002:str',
        construct_yaml_str
    )

    return yaml.load(stream, Loader)
