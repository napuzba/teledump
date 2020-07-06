""" This Module contains classes related to Metadata Files"""

import codecs
import errno
import json
import logging
import os.path

from . import ChatDumpSettings
from ..exceptions import MetaFileError


class ChatDumpMetaFile:
    """ Metadata file CRUD """
    key_version        : int = 'version'
    key_chatName       : str = "chat-name"
    key_LastMessageId  : str = "latest-message-id"
    key_exporter       : str = "exporter-name"
    key_exporterConfig : str = "exporter-config"
    key_filter         : str = "filter-name"


    def __init__(self, path : str):
        self._logger : logging.Logger = logging.getLogger(__name__)
        self._path : str  = path + '.meta'
        self._data : dict = {}


    def merge(self, settings: ChatDumpSettings) -> None:
        if not self._data:
            self._load()
        settings.chatName      = self._data[ChatDumpMetaFile.key_chatName]
        settings.idLastMessage = self._data[ChatDumpMetaFile.key_LastMessageId]
        settings.exporter      = self._data[ChatDumpMetaFile.key_exporter]
        settings.exporterConfig= self._data[ChatDumpMetaFile.key_exporterConfig]
        settings.filter        = self._data[ChatDumpMetaFile.key_filter]

    def _load(self) -> None:
        """ Loads metadata from file """
        try:
            self._logger.debug('Load metafile %s.', self._path)
            with codecs.open(self._path, 'r', 'utf-8') as ff:
                self._data = json.load(ff)
                # TODO Validate Meta Dict
        except OSError as ex:
            msg = 'Unable to open the metadata file "{}". {}'.format(self._path, ex.strerror)
            raise MetaFileError(msg) from ex
        except ValueError as ex:
            msg = 'Unable to load the metadata file "{}". AttributeError: {}'.format(self._path, ex)
            raise MetaFileError(msg) from ex

    def delete(self) -> None:
        """ Delete metafile if running in CONTINUE mode """
        try:
            self._logger.debug('Delete old metadata file %s.', self._path)
            os.remove(self._path)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                msg = 'Failed to delete old metadata file. {}'.format(ex.strerror)
                raise MetaFileError(msg)

    def save(self, data : dict) -> None:
        """ Save metafile to file"""
        try:
            self._logger.debug('Save new metadata file %s.', self._path)
            self._add_version()
            self._add_key(data, ChatDumpMetaFile.key_chatName)
            self._add_key(data, ChatDumpMetaFile.key_LastMessageId)
            self._add_key(data, ChatDumpMetaFile.key_exporter)
            self._add_key(data, ChatDumpMetaFile.key_exporterConfig)
            self._add_key(data, ChatDumpMetaFile.key_filter)
            with open(self._path, 'w') as mf:
                json.dump(self._data, mf, indent=4, sort_keys=False)
        except OSError as ex:
            msg = 'Failed to write the metadata file. {}'.format(ex.strerror);
            raise MetaFileError(msg)

    def _add_key(self, data: dict, key: str) -> None:
        if key in data:
            self._data[key] = data[key]

    def _add_version(self) -> None:
        if not self._data:
            self._data = {}
        self._data[ChatDumpMetaFile.key_version] = 1
