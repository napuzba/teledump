import argparse

class CustomArgumentParser(argparse.ArgumentParser):
  """ Custom ArgumentParser.
      Outputs raw 'usage' text and omits other sections.
  """

  def format_help(self):
    formatter = self._get_formatter()
    # usage
    formatter.add_usage(self.usage, self._actions,
                        self._mutually_exclusive_groups)
    return formatter.format_help()
