class Processor:
    """ 
    Generic parent class for classes that processes raw data downloaded for
    any one of the various websites for clinical trials listings.
    """

    def process_and_load_df(self, filepath_or_buffer):
        """
        Processes the specified file; returns a pandas DataFrame containing the
        processed data.

        Args:
            filepath_or_buffer: Path to the file to be processed, or
                a buffer containing the contents of the file to be
                processed in memory.
        """
        raise NotImplementedError