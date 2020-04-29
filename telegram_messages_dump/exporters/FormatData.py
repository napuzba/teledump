from telethon.tl.custom.message import Message

class FormatData(object):
    """ json exporter plugin.
        By convention it has to be called exactly the same as its file name.
        (Apart from .py extention)
    """

    def __init__(self, msg : Message = None):
        """ constructor """
        self.name : str = None
        self.caption : str = None
        self.content : str = None
        self.re_id_str : str = None
        self.is_sent_by_bot : str = None
        self.is_contains_media : str = None
        self.media_content : str = None

        if msg != None:
            self.parse(msg)

    def parse(self,msg: Message) -> None:
        """ Extracts user name from 'sender', message caption and message content from msg.
            :param msg: Raw message object.

            :return
                (...) tuple of message attributes
        """
        sender = msg.sender

        # Get the name of the sender if any
        is_sent_by_bot = None
        if sender:
            self.name = getattr(sender, 'username', None)
            if not self.name:
                self.name = getattr(sender, 'title', None)
                if not self.name:
                    self.name = (sender.first_name or "") + " " + (sender.last_name or "")
                    self.name = self.name.strip()
                if not self.name:
                    self.name = '???'
            is_sent_by_bot = getattr(sender, 'bot', None)
        else:
            self.name = '???'

        self.caption = None
        if hasattr(msg, 'message'):
            self.content = msg.message
        elif hasattr(msg, 'action'):
            self.content = str(msg.action)
        else:
            # Unknown message, simply print its class name
            self.content = type(msg).__name__

        self.re_id_str = ''
        if hasattr(msg, 'reply_to_msg_id') and msg.reply_to_msg_id is not None:
            self.re_id_str = str(msg.reply_to_msg_id)

        self.is_contains_media = False
        self.media_content = None
        # Format the message content
        if getattr(msg, 'media', None):
            # The media may or may not have a caption
            self.is_contains_media = True
            self.caption = getattr(msg.media, 'caption', '')
            self.media_content = '<{}> {}'.format(
                type(msg.media).__name__, self.caption)
