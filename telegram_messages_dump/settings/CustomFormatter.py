import argparse
class CustomFormatter(argparse.HelpFormatter):
  """ Custom formatter for setting argparse formatter_class.
      It only outputs raw 'usage' text and omits other sections
      (e.g. positional, optional params and epilog).
  """

  def __init__(self, prog=''):
    argparse.HelpFormatter.__init__(
      self, prog, max_help_position=100, width=150)

  def add_usage(self, usage, actions, groups, prefix=None):
    if usage is not argparse.SUPPRESS:
      args = usage, actions, groups, ''
      self._add_item(self._format_usage, args)

  def _format_usage(self, usage, actions, groups, prefix):
    # if usage is specified, use that
    if usage is not None:
      usage = usage % dict(prog=self._prog)

    return "\n\r%s\n\r" % usage

