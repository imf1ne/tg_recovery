from abc import ABC, abstractmethod
import random
import string


class Media(ABC):
    def __init__(self, media, msg_id):
        # self.main_type = media['_']
        self.msg_id = msg_id
        self.size = self.get_filesize(media)
        self.filename = self.get_filename(media)

    @abstractmethod
    def get_filename(self, media):
        pass

    @abstractmethod
    def get_filesize(self, media):
        pass


class MediaEmpty(Media):
    def get_filename(self, media):
        return None

    def get_filesize(self, media):
        return None


class MediaUnknown(Media):
    def get_filename(self, media):
        return 'Type-unknown.no'

    def get_filesize(self, media):
        return None


class MessageMediaDocument(Media):
    def __init__(self, media, msg_id):
        super().__init__(media, msg_id)

    def get_filename(self, media):
        self.mime_type = media['document']['mime_type']  # Тип документа
        if 'image' in self.mime_type:
            d = DocumentPng(media)
        elif self.mime_type == 'audio/ogg':
            d = DocumentVoice(media)
        elif self.mime_type == 'audio/mpeg':
            d = DocumentVoice(media)
        else:
            d = DocumentUnsupported(media)

        return d.filename

    def get_filesize(self, media):
        return media['document']['size']


class MessageMediaPhoto(Media):
    def get_filename(self, media):
        return str(self.msg_id) + '.jpg'

    def get_filesize(self, media):
        for a in media['photo']['sizes']:
            if a['_'] == 'PhotoSize':
                return a['size']


class Document(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()


class DocumentPng(Document):
    def __init__(self, media):
        self.filename = 'no-name'
        for a in media['document']['attributes']:
            if a['_'] == 'DocumentAttributeFilename':
                self.filename = a['file_name']
                break


class DocumentVoice(Document):
    def __init__(self, media):
        self.filename = ''.join(random.choices(string.ascii_lowercase, k=10), '.oga')


class DocumentAudioMpeg(Document):
    def __init__(self, media):
        self.filename = 'no-name'
        for a in media['document']['attributes']:
            if a['_'] == 'DocumentAttributeFilename':
                self.filename = a['file_name']
                break


class DocumentUnsupported(Document):
    def __init__(self, media):
        self.filename = 'Type-unknown.no'
