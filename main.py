import socket
import os
import json, time
import _thread

class ReadOnlyIRCBot(object):
    HOST = 'irc.chat.twitch.tv'
    PORT = 6667

    def __init__(self, scrape_list, channel, nick=None, oauth_token=None):
        # Initial vars
        self.counter = 0
        self.channel = channel
        self.oauth_token = oauth_token
        self.read_buffer = ""
        self.nick = nick
        self.joined_room = False
        self.scrape_list = scrape_list

        # List counter

        if scrape_list is None:
            raise ValueError("scrape_list is needed for returning messages")
        elif type(scrape_list) != list:
            raise ValueError("scrape_list must be a list")

        if nick is None:
            self.nick = channel

        if oauth_token is None:
            oauth_token = os.getenv("TWITCH_KEY")
            if oauth_token == '':
                raise Exception("No valid twitch key for oauth token, please supply it or set as env.")

        self.socket = socket.socket()
        self.socket.connect((self.HOST, self.PORT))

    def _connect_to_server(self):
        # Authenticate
        self._send('PASS oauth:{}\r\n'.format(self.oauth_token))
        self._send('NICK {}\r\n'.format(self.nick))
        print("authenticated")

    def _join_chatroom(self):
        self._send('JOIN #{}\r\n'.format(self.channel))
        print("sent channel join")

    def _send(self, message):
        self.socket.send(bytes(message, 'UTF-8'))

    def send_list(self, listy):
        # API request to separate flask service?
        pass

    def run(self):
        self._connect_to_server()
        # Main run loop
        while True:
            self.read_buffer = self.read_buffer + self.socket.recv(1024).decode('UTF-8')
            # temporary split
            temp = str.split(self.read_buffer, '\n')
            self.read_buffer = temp.pop()

            for line in temp:
                line = line.rstrip()
                line = line.split(':')
                # print(line)

                if line[0] == "PING ":
                    self.socket.send(bytes("PONG {}\r\n".format(line[1]), 'UTF-8'))
                    print("sent PONG!")
                # If client get this, then we are connected
                elif line[1] == 'tmi.twitch.tv 376 %s ' % self.nick:
                    self.connected = True
                    self._join_chatroom()

                if len(line) == 3:
                    if line[2] == 'End of /NAMES list':
                        self.joined_room = True
                    if self.joined_room:
                        # Set msg counter
                        self.counter += 1
                        # print msg to console
                        print("message from channel %s" % self.channel + ">" + line[2])
                        # copy message value to list, no sort
                        self.scrape_list.append(line[2])

                if self.counter >= 100:
                    # Send list and set counter and list to empty values
                    self.send_list(self.scrape_list)
                    self.counter = 0
                    self.scrape_list = []
                    print("sent messages, cleared messages")

                print("self_counter is : %s" % self.counter)


class EmoteWeights(object):
    # Disgustingly simple word-counter weights for Twitch Chat.
    def __init__(self, coming_list,based_weights):
        # Input list of comments
        self.coming_list = coming_list
        # Output json payload
        self.out_json = based_weights
        # Json-defined weights for every single emote in chat
        self.based_weights = based_weights
        # Example json would be {"emote":"characteristic"}
        # the more emotes there are, more of char there is
        # simply count and weight for our coming_list, send api request containing result to our django app
        # make a /save endpoint there which queues all incoming requests.

    def run(self):
        #  just count all emotes in last 100 messages
        print(self.coming_list)
        self.coming_list.split()

        for i in self.based_weights.keys():
            # Count how many and put them on the out
            amount = self.coming_list.count(self.based_weights[i])
            self.out_json[i] = amount
            print(json.dumps(self.out_json))


if __name__ == '__main__':
    listy = []
    listy_results = []
    weights = {"emote":"1","emote2":"2"}

    irc_bot = ReadOnlyIRCBot(scrape_list=listy, nick="", channel='',
                             oauth_token='')
    irc_bot.run()