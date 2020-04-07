import logging
import os

import iridauploader.model as model
import iridauploader.progress as progress

from iridauploader.parsers import exceptions
from iridauploader.parsers import common
from iridauploader.parsers.miseq import sample_parser, validation


class Parser:

    SAMPLE_SHEET_FILE_NAME = 'SampleSheet.csv'
    UPLOAD_COMPLETE_FILE_NAME = 'CompletedJobInfo.xml'

    @staticmethod
    def get_required_file_list():
        """
        Returns a list of files that are required for a run directory to be considered valid
        :return: [files_names]
        """
        return [
            Parser.SAMPLE_SHEET_FILE_NAME,
            Parser.UPLOAD_COMPLETE_FILE_NAME
        ]

    @staticmethod
    def get_relative_data_directory():
        """
        Returns path to the sequence file directory, relative to the Sample Sheet

        This is not used in the application but is useful for scripting and cloud deployment

        :return: a string which represents the concatenated path components, as per os.path.join
        """
        data_dir = os.path.join("Data", "Intensities", "BaseCalls")
        return data_dir

    @staticmethod
    def get_full_data_directory(sample_sheet):
        """
        Returns the path to where the sequence data files can be found, including the sample_sheet directory

        :param sample_sheet: Sample sheet acts as the starting point for the data directory
        :return: a string which represents the concatenated path components, as per os.path.join
        """
        sample_sheet_dir = os.path.dirname(sample_sheet)
        data_dir = os.path.join(sample_sheet_dir, Parser.get_relative_data_directory())
        return data_dir

    @staticmethod
    def find_runs(directory):
        """
        find a list of run directories in the directory given

        :param directory:
        :return: list of DirectoryStatus objects
        """
        logging.info("Looking for runs in {}".format(directory))

        runs = []
        directory_list = common.find_directory_list(directory)
        for d in directory_list:
            runs.append(progress.get_directory_status(d, Parser.get_required_file_list()))

        return runs

    @staticmethod
    def find_single_run(directory):
        """
        Find a run in the base directory given

        :param directory:
        :return: DirectoryStatus object
        """
        logging.info("looking for run in {}".format(directory))

        return progress.get_directory_status(directory, Parser.get_required_file_list())

    @staticmethod
    def get_sample_sheet(directory):
        """
        gets the sample sheet file path from a given run directory

        :param directory:
        :return:
        """
        logging.info("Looking for sample sheet in {}".format(directory))

        # Checks if we can access to the given directory, return empty and log a warning if we cannot.
        if not os.access(directory, os.W_OK):
            logging.error(("The directory is not accessible, can not parse samples from this directory {}"
                           "".format(directory), directory))
            raise exceptions.DirectoryError("The directory is not accessible, "
                                            "can not parse samples from this directory {}".format(directory), directory)

        sample_sheet_file_name = Parser.SAMPLE_SHEET_FILE_NAME
        file_list = common.get_file_list(directory)  # Gets the list of files in the directory
        if sample_sheet_file_name not in file_list:
            logging.error("No sample sheet file in the MiSeq format found")
            raise exceptions.DirectoryError("The directory {} has no sample sheet file in the MiSeq format"
                                            " with the name {}"
                                            .format(directory, sample_sheet_file_name), directory)
        else:
            logging.debug("Sample sheet found")
            return os.path.join(directory, sample_sheet_file_name)

    @staticmethod
    def get_sequencing_run(sample_sheet, run_data_directory=None, run_data_directory_file_list=None):
        """
        Does local validation on the integrety of the run directory / sample sheet

        Throws a ValidationError with a valadation result attached if it cannot make a sequencing run

        :param sample_sheet: Sample Sheet File
        :param run_data_directory: Optional: Directory (including run directory) to data files.
                                   Can be provided for bypassing os calls when developing on cloud systems
        :param run_data_directory_file_list: Optional: List of files in data directory.
                                             Can be provided for bypassing os calls when developing on cloud systems
        :return: SequencingRun
        """

        # get data directory and file list
        if run_data_directory is None:
            run_data_directory = Parser.get_full_data_directory(sample_sheet)
        if run_data_directory_file_list is None:
            run_data_directory_file_list = common.get_file_list(run_data_directory)

        # Try to get the sample sheet, validate that the sample sheet is valid
        validation_result = validation.validate_sample_sheet(sample_sheet)
        if not validation_result.is_valid():
            logging.error("Errors occurred while getting sample sheet")
            raise exceptions.ValidationError("Errors occurred while getting sample sheet", validation_result)

        # Try to parse the meta data from the sample sheet, throw validation error if errors occur
        validation_result = model.ValidationResult()
        try:
            run_metadata = sample_parser.parse_metadata(sample_sheet)
        except exceptions.SampleSheetError as error:
            validation_result.add_error(error)
            logging.error("Errors occurred while parsing metadata")
            raise exceptions.ValidationError("Errors occurred while parsing metadata", validation_result)

        # Try to build sequencing run from sample sheet & meta data, raise validation error if errors occur
        try:
            sample_list = sample_parser.parse_sample_list(sample_sheet, run_data_directory, run_data_directory_file_list)
            sequencing_run = common.build_sequencing_run_from_samples(sample_list, run_metadata)
        except exceptions.SequenceFileError as error:
            validation_result.add_error(error)
            logging.error("Errors occurred while building sequence run from sample sheet")
            raise exceptions.ValidationError("Errors occurred while building sequence run from sample sheet",
                                             validation_result)

        return sequencing_run
