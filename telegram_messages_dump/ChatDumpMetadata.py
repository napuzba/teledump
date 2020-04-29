#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This Module contains classes related to Metadata Files"""

import os.path
import errno
import codecs
import json
import logging
from .exceptions import MetadataError
from .settings   import ChatDumpSettings


class DumpMetadata:
    """ Metadata file CRUD """
    key_version       : int = 'version'
    key_chatName      : str = "chat-name"
    key_LastMessageId : str = "latest-message-id"
    key_exporter      : str = "exporter-name"


    def __init__(self, path : str):
        self._logger : logging.Logger = logging.getLogger(__name__)
        self._path : str  = path + '.meta'
        self._data : dict = {}


    def merge(self, settings: ChatDumpSettings) -> None:
        if not self._data:
            self._load()
        settings.chat_name       = self._data[DumpMetadata.key_chatName]
        settings.last_message_id = self._data[DumpMetadata.key_LastMessageId]
        settings.exporter        = self._data[DumpMetadata.key_exporter]

    def _load(self) -> None:
        """ Loads metadata from file """
        try:
            self._logger.debug('Load metafile %s.', self._path)
            with codecs.open(self._path, 'r', 'utf-8') as ff:
                self._data = json.load(ff)
                # TODO Validate Meta Dict
        except OSError as ex:
            msg = 'Unable to open the metadata file "{}". {}'.format(self._path, ex.strerror)
            raise MetadataError(msg) from ex
        except ValueError as ex:
            msg = 'Unable to load the metadata file "{}". AttributeError: {}'.format(self._path, ex)
            raise MetadataError(msg) from ex

    def delete(self) -> None:
        """ Delete metafile if running in CONTINUE mode """
        try:
            self._logger.debug('Delete old metadata file %s.', self._path)
            os.remove(self._path)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                msg = 'Failed to delete old metadata file. {}'.format(ex.strerror)
                raise MetadataError(msg)

    def save(self, data : dict) -> None:
        """ Save metafile to file"""
        try:
            self._logger.debug('Save new metadata file %s.', self._path)
            self._add_version()
            self._add_key(data, DumpMetadata.key_chatName)
            self._add_key(data, DumpMetadata.key_LastMessageId)
            self._add_key(data, DumpMetadata.key_exporter)
            with open(self._path, 'w') as mf:
                json.dump(self._data, mf, indent=4, sort_keys=False)
        except OSError as ex:
            msg = 'Failed to write the metadata file. {}'.format(ex.strerror);
            raise MetadataError(msg)

    def _add_key(self, data: dict, key: str) -> None:
        if key in data:
            self._data[key] = data[key]

    def _add_version(self) -> None:
        if not self._data:
            self._data = {}
        self._data[DumpMetadata.key_version] = 1
