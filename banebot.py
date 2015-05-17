

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

# system imports
import time, sys, unicodedata, random

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    nickname = 'BaneCat' # nickname
    password = '' # server pass
    realname = "Backbreaker"
    nickservPass = 'password'
    
    batkey = {
            "key to happiness" : "#firstbatproblems"    
    }

    quotes = {

            "bat" : "I WILL BREAK THE BAT!",
            "fire" : "Yes. The fire rises.",
            "die" : "You don't fear death... You welcome it. Your punishment must be more severe.",
            "kill" : "You don't fear death... You welcome it. Your punishment must be more severe.",
            "death" : "You don't fear death... You welcome it. Your punishment must be more severe.",
            "evil" : "I'm necessary evil!",
            "youtube" : "https://www.youtube.com/watch?v=5ywjpbThDpE"
        }
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print "connectionMade"
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        #self.msg('NickServ', 'REGISTER %s RMS@GNUplusLinux.com' % self.nickservPass)
        self.msg('NickServ', 'IDENTIFY %s' % self.nickservPass)
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % self.factory.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""

        
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "Bro."
            self.msg(user, msg)
            return

        for trig in self.batkey.keys():
            if trig in msg.lower():
                thekey = self.batkey[trig]
                self.msg(user, thekey)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                break

        for trigger in self.quotes.keys():
            if trigger in msg.lower():
                quote = self.quotes[trigger]
                msg = "%s: %s" % (user, quote)
                self.msg(channel, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                break

    def alterCollidedNick(self, nickname):
        return nickname+'_'

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'
        
class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """
    protocol = LogBot

    def __init__(self, filename):
        self.channel = '#chan' #channel
        self.filename = filename

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)
    
    # create factory protocol and application
    f = LogBotFactory(sys.argv[1])

    # connect factory to this host and port
    hostname = 'irc.hostname.com' # irc-server-hostname
    port = 6697
    reactor.connectSSL(hostname, port, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
