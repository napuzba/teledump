class ExporterContext:
    """ Exporter context """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self):
        # Is processing the first record
        self.isFirst : bool = False
        # Is processing the last record
        self.isLast : bool = True
        # Is working in continue/incremental mode
        self.isContinue : bool = False
