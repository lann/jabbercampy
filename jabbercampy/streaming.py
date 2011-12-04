import base64
import Queue
import socket
import threading
import urllib2

from jabbercampy import __version__

STREAMING_URL_PATTERN = 'https://streaming.campfirenow.com/room/%d/live.json'

USER_AGENT = 'Python-urllib/%s jabbercampy/%s' % (
    urllib2.__version__, __version__)

class StreamingThread(threading.Thread):
    __die = False

    def __init__(self, token, room_id, *args, **kwargs):
        self.queue = Queue.Queue()

        auth_header = 'Basic %s' % base64.b64encode('%s:' % token)
        self.request = urllib2.Request(
            STREAMING_URL_PATTERN % room_id,
            headers={
                'User-Agent': USER_AGENT,
                'Authorization': auth_header
            })

        super(StreamingThread, self).__init__(*args, **kwargs)

    def run(self):
        try:
            resp = urllib2.urlopen(self.request)

            # Ugh
            socket.fromfd(
                resp.fileno(), socket.AF_INET, socket.SOCK_STREAM
                ).settimeout(1)

            while not self.__die:
                try:
                    char = resp.read(1)
                except urllib2.socket.timeout:
                    continue

                # Eat spaces between data chunks
                if not char.isspace():
                    buf = [char]

                    # Data chunks are terminated with \r
                    while char != '\r':
                        if self.__die:
                            break

                        try:
                            char = resp.read(1)
                        except urllib2.socket.timeout:
                            continue

                        buf.append(char)

                    else:
                        self.queue.put(''.join(buf))

        except Exception, e:
            self.queue.put(e)

        finally:
            self.queue.put(None)

    def die(self):
        self.__die = True

    @classmethod
    def from_pinder_room(cls, room, *args, **kwargs):
        return cls(room._campfire._token, room.id, *args, **kwargs)
