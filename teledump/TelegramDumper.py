#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is a main Module that contains code
    that fetches messages from Telegram and do processing.
"""

import codecs
import logging
import os
import os.path
import sys
import tempfile
from collections import deque
from getpass import getpass
from time import sleep
from typing import Deque
from typing import TextIO

from telethon import TelegramClient,sync  # pylint: disable=unused-import
from telethon.errors import (FloodWaitError,
                             SessionPasswordNeededError,
                             UsernameNotOccupiedError,
                             UsernameInvalidError)
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import Channel

from .exceptions import DumpingError
from .exceptions import MetaFileError
from .exporters import Exporter
from .filters import Filter
from .exporters import ExporterContext
from .settings import ChatDumpMetaFile
from .settings import ChatDumpSettings
from .utils import JOIN_CHAT_PREFIX_URL


class TelegramDumper(TelegramClient):
    """ Authenticates and opens new session. Retrieves message history for a chat. """

    def __init__(self, session_user_id, settings : ChatDumpSettings, chatMeta: ChatDumpMetaFile, exporter: Exporter, filter : Filter ):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing session...')
        super().__init__(
            session_user_id,
            settings.api_id,
            settings.api_hash,
            timeout=40, #seconds
            proxy=None
        )

        # Settings as specified by user or defaults or from metadata
        self.settings : ChatDumpSettings = settings
        # Metadata that was possibly loaded from .meta file and will be saved there
        self.chatMeta : ChatDumpMetaFile = chatMeta
        # Exporter object that converts msg -> string
        self.exporter : Exporter = exporter
        self.filter   : Filter = filter

        # The context that will be passed to the exporter
        self.context : ExporterContext = ExporterContext()
        self.context.isContinue = self.settings.isIncremental
        # How many massages user wants to be dumped
        # explicit --limit, or default of 100 or unlimited (int.Max)
        self.messageToFetch : int = 0

        # Messages page offset for fetching
        self.idPageOffset : int = 0

        # A list of paths to the temp files
        self.tempFiles : Deque[str] = deque()

        # Actual lattets message id that was prossessed since the dumper started running
        self.idLastMessage : int = self.settings.idLastMessage

        # The number of messages written into a resulting file de-facto
        self.totalSaved : int = 0

    def run(self) -> int:
        """ Dumps all desired chat messages into a file """
        rc = 0
        try:
            self._cnnect()
            try:
                chatObj = self._getChannel()
            except ValueError as ex:
                rc = 1
                self.logger.error('%s', ex, exc_info=self.logger.level > logging.INFO)
                return rc
            # Fetch history in chunks and save it into a resulting file
            self._dump(chatObj)
        except (DumpingError, MetaFileError) as ex:
            self.logger.error('%s', ex, exc_info=self.logger.level > logging.INFO)
            rc = 1
        except KeyboardInterrupt:
            self.print("Received a user's request to interrupt, stopping…")
            rc = 1
        except Exception as ex:  # pylint: disable=broad-except
            self.logger.error('Uncaught exception occured. %s', ex, exc_info=self.logger.level > logging.INFO)
            rc = 1
        finally:
            self.logger.debug('Make sure there are no temp files left undeleted.')
            # Clear temp files if any
            while self.tempFiles:
                try:
                    os.remove(self.tempFiles.pop().name)
                except Exception:  # pylint: disable=broad-except
                    pass

        if self.settings.isClean:
            try:
                # TODO
                # self.log_out()
                self.logger.info('Session data cleared.')
            except Exception:  # pylint: disable=broad-except
                self.print('Failed to logout and clean session data.')

        self.print('{} messages were successfully written in the resulting file. Done!', self.totalSaved)
        return rc

    def _cnnect(self) -> None:
        """ Connect to the Telegram server and Authenticate. """
        self.print('Connecting to Telegram servers...')
        if not self.connect():
            self.print('Initial connection failed.')
        # Then, ensure we're authorized and have access
        if not self.is_user_authorized():
            self.print('First run. Sending code request...')
            self.send_code_request(self.settings.phoneNum)
            selfUser = None
            while selfUser is None:
                code = input('Enter the code you just received: ')
                try:
                    selfUser = self.sign_in(self.settings.phoneNum, code)
                    # Two-step verification may be enabled
                except SessionPasswordNeededError:
                    pw = getpass("Two step verification is enabled. Please enter your password: ")
                    selfUser = self.sign_in(password=pw)

    def _getChannel(self) -> Channel:
        """ Returns telethon.tl.types.Channel object resolved from chat_name
            at Telegram server
        """
        name = self.settings.chatName

        # For private channуls try to resolve channel peer object from its invitation link
        # Note: it will only work if the login user has already joined the private channel.
        # Otherwise, get_entity will throw ValueError
        if name.startswith(JOIN_CHAT_PREFIX_URL):
            self.logger.debug('Trying to resolve as invite url.')
            try:
                peer = self.get_entity(name)
                if peer:
                    self.print('Invitation link "{}" resolved into channel id={}',name, peer.id)
                    return peer
            except ValueError as ex:
                self.logger.debug( 'Failed to resolve "%s" as an invitation link. %s', self.settings.chatName, ex, exc_info=self.logger.level > logging.INFO)

        if name.startswith('@'):
            name = name[1:]
            self.logger.debug('Trying ResolveUsernameRequest().')
            try:
                peer = self(ResolveUsernameRequest(name))
                if peer.chats is not None and peer.chats:
                    self.print('Chat name "{}" resolved into channel id={}', name, peer.chats[0].id )
                    return peer.chats[0]
                if peer.users is not None and peer.users:
                    self.print('User name "{}" resolved into channel id={}', name, peer.users[0].id )
                    return peer.users[0]
            except (UsernameNotOccupiedError, UsernameInvalidError) as ex:
                self.logger.debug('Failed to resolve "%s" as @-chat-name. %s', self.settings.chatName, ex, exc_info=self.logger.level > logging.INFO)

        # Search in dialogs first, this way we will find private groups and
        # channels.
        self.logger.debug('Fetch loggedin user`s dialogs')
        dialogs_count = self.get_dialogs(0).total
        self.logger.info('%s user`s dialogs found', dialogs_count)
        dialogs = self.get_dialogs(limit=None)
        self.logger.debug('%s dialogs fetched.', len(dialogs))
        for dialog in dialogs:
            if dialog.name == name:
                self.print('Dialog title "{}" resolved into channel id={}', name, dialog.entity.id)
                return dialog.entity
            if hasattr(dialog.entity, 'username') and dialog.entity.username == name:
                self.print('Dialog username "{}" resolved into channel id={}', name, dialog.entity.id)
                return dialog.entity
            if name.startswith('@') and dialog.entity.username == name[1:]:
                self.print('Dialog username "{}" resolved into channel id={}', name, dialog.entity.id)
                return dialog.entity
        self.logger.debug('Specified chat name was not found among dialogs.')

        raise ValueError('Failed to resolve dialogue/chat name "{}".'.format(name))

    def _fetch(self, peer, buffer : Deque[str]) -> int:
        """ Retrieves a number (100) of messages from Telegram's DC and adds them to 'buffer'.
            :param peer:        Chat/Channel object
            :param buffer:      buffer where to place retrieved messages

            :return The latest/biggest Message ID that successfully went into buffer,
                    or -1 if there are no more messages.
        """
        messages = []

        # First retrieve the messages and some information
        # make 5 attempts
        for _ in range(0, 5):
            try:
                # NOTE: Telethon will make 5 attempts to reconnect before failing
                limit = 100
                if self.messageToFetch > 1000:
                    limit = 1000
                messages = self.get_messages(peer, limit=limit, offset_id=self.idPageOffset)
                if messages.total > 0 and messages:
                    self.print('{2:5} To Find - Fetch messages with ids {0:6} - {1:6} ...', messages[0].id, messages[-1].id , self.messageToFetch)
            except FloodWaitError as ex:
                self.print('FloodWaitError detected. Sleep for {} sec before reconnecting! \n', ex.seconds)
                sleep(ex.seconds)
                self._cnnect()
                continue
            break

        idLastMessage = -1 \
            if not messages or self.settings.idLastMessage >= messages[0].id \
            else messages[0].id

        # Iterate over all (in reverse order so the latest appear
        # the last in the console) and print them with format provided by exporter.
        for msg in messages:
            self.context.isFirst = (self.messageToFetch == 1)

            if not self.filter.valid(msg):
                self.idPageOffset = msg.id
                continue

            if self.settings.idLastMessage >= msg.id:
                self.messageToFetch = 0
                break

            msg_dump_str = self.exporter.format(msg, self.context)

            buffer.append(msg_dump_str)

            self.messageToFetch -= 1
            self.idPageOffset = msg.id
            self.context.isLast = False
            if self.messageToFetch == 0:
                break

        return idLastMessage

    def _dump(self, peer) -> None:
        """ Retrieves messages in small chunks (Default: 100) and saves them in in-memory 'buffer'.
            When buffer reaches '1000' messages they are saved into intermediate temp file.
            In the end messages from all the temp files are being moved into resulting file in
            ascending order along with the remaining ones in 'buffer'.
            After all, temp files are deleted.

             :param peer: Chat/Channel object that contains the message history of interest

             :return  Number of files that were saved into resulting file
        """
        self.messageToFetch = self.settings.limit \
            if self.settings.limit != -1\
            and not self.settings.limit == 0\
            and not self.settings.isIncremental\
            else sys.maxsize

        self._preconditions()

        # Current buffer of messages, that will be batched into a temp file
        # or otherwise written directly into the resulting file if there are too few of them
        # to form a batch of size 1000.
        buffer = deque()

        # Delete old metafile in Continue mode
        if not self.settings.isIncremental:
            self.chatMeta.delete()

        tempMetaFiles = deque()  # a list of meta info about batches

        # process messages until either all message count requested by user are retrieved
        # or offset_id reaches msg_id=1 - the head of a channel message history
        try:
            while self.messageToFetch > 0:
                # slip for a few seconds to avoid flood ban
                sleep(2)
                latest_message_id_fetched = self._fetch(peer, buffer)
                # This is for the case when buffer with fewer than 1000 records
                # Relies on the fact that `_fetch_messages_from_server` returns messages
                # in reverse order
                if self.idLastMessage < latest_message_id_fetched:
                    self.idLastMessage = latest_message_id_fetched
                # when buffer is full, flush it into a temp file
                # Assume that once a message got into temp file it will be counted as successful
                # 'output_total_count'. This has to be improved.
                if len(buffer) >= 1000:
                    self._saveTempFile(buffer)
                    tempMetaFiles.append(latest_message_id_fetched)

                # break if the very beginning of channel history is reached
                if latest_message_id_fetched == -1 or self.idPageOffset <= 1:
                    break
        except RuntimeError as ex:
            self.print('Fetching messages from server failed. {}',str(ex))
            self.print('Warn: The resulting file will contain partial/incomplete data.')

        # Write all chunks into resulting file
        self.print('Merging results into an output file.')
        try:
            self._saveFinalFile(buffer, tempMetaFiles)
        except OSError as ex:
            raise DumpingError("Dumping to a final file failed.") from ex

        data = {}
        data[ChatDumpMetaFile.key_chatName      ] = self.settings.chatName
        data[ChatDumpMetaFile.key_LastMessageId ] = self.idLastMessage
        data[ChatDumpMetaFile.key_exporter      ] = self.settings.exporter
        data[ChatDumpMetaFile.key_exporterConfig] = self.settings.exporterConfig
        data[ChatDumpMetaFile.key_filter        ] = self.settings.filter
        self.chatMeta.save(data)

    def _saveTempFile(self, buffer : Deque[str]) -> None:
        """ Flush buffer into a new temp file """
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as ff:
            self.totalSaved += self._saveFile(ff, buffer)
            self.tempFiles.append(ff)

    def _saveFile(self, outFile: TextIO, buffer: Deque[str]) -> int:
        """ Flush buffer into a file stream """
        count = 0
        while buffer:
            count += 1
            cur_message = buffer.pop()
            print(cur_message, file=outFile)
        return count

    def _saveFinalFile(self, buffer : Deque[str], temp_files_list_meta : Deque[str]) -> None:
        result_file_mode = 'a' if self.settings.idLastMessage > -1 else 'w'
        with codecs.open(self.settings.outFile, result_file_mode, 'utf-8') as ff:
            if self.settings.isAddbom:
                ff.write(codecs.BOM_UTF8.decode())

            self.exporter.begin_final_file(ff, self.context)
            # flush what's left in the mem buffer into resulting file
            self.totalSaved += self._saveFile(ff, buffer)
            self._mergeToFinalFile(ff, temp_files_list_meta)

    def _mergeToFinalFile(self, outFile : TextIO, temp_files_list_meta : Deque[str]) -> None:
        """ merge all temp files into final one and delete them """
        while self.tempFiles:
            tf = self.tempFiles.pop()
            with codecs.open(tf.name, 'r', 'utf-8') as ctf:
                for line in ctf.readlines():
                    print(line, file=outFile, end='')
            # delete temp file
            self.logger.debug("Delete temp file %s", tf.name)
            tf.close()
            os.remove(tf.name)
            # update the latest_message_id metadata
            batch_latest_message_id = temp_files_list_meta.pop()
            if batch_latest_message_id > self.idLastMessage:
                self.idLastMessage = batch_latest_message_id

    def _preconditions(self) -> None:
        """ Check preconditions before processing data """
        out_file_path = self.settings.outFile
        if self.settings.isIncremental:
            # In incrimental mode
            self.print('Switching to incremental mode.')
            self.logger.debug('Checking if output file exists.')
            if not os.path.exists(out_file_path):
                msg = 'Error: Output file does not exist. Path="{}"'.format(out_file_path)
                raise DumpingError(msg)
            self.print('Dumping messages newer than {} using "{}" dumper.', self.settings.idLastMessage, self.settings.exporter)
        else:
            # In NONE-incrimental mode
            if os.path.exists(out_file_path):
                self.print('Warning: The output file already exists.')
                if not self._confirm('Are you sure you want to overwrite it? [y/n]'):
                    raise DumpingError("Terminating on user's request...")
            # Check if output file can be created/overwritten
            try:
                with open(out_file_path, mode='w+'):
                    pass
            except OSError as ex:
                msg = 'Output file path "{}" is invalid. {}'.format(out_file_path, ex.strerror)
                raise DumpingError(msg)
            self.print('Dumping {} messages into "{}" file ...', 'all' if self.messageToFetch == sys.maxsize else self.messageToFetch, out_file_path)

    def _confirm(self, msg: str) -> bool:
        """ Get confirmation from user """
        if self.settings.isQuiet:
            return True
        response = input(msg).lower().strip()
        return response == 'y' or response == 'yes'

    def print(self, msg : str, *args, **kwargs):
        """Safe Print (handle UnicodeEncodeErrors on some terminals)"""
        try:
            msg = msg.format(*args)
            print(msg)
        except UnicodeEncodeError:
            msg = msg.encode('utf-8', errors='ignore').decode('ascii', errors='ignore')
            print(msg)
