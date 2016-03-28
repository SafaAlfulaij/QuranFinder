
# Copyright 2016 Safa AlFulaij <safa1996alfulaij@gmail.com>
#
# This file is part of QuranFinder.
#
# QuranFinder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QuranFinder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QuranFinder.  If not, see <http://www.gnu.org/licenses/>.

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('QuranFinder')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

API_URL = "http://quranapi.azurewebsites.net/api/verse/"
import requests

class qdata():
    def __init__(self, chapter, ayah, lang):
        self.supportedLangs = ("en","ar")

        if (chapter > 114 or chapter < 1):
            raise ValueError("Invalid Surah number.")
        if(lang not in self.supportedLangs):
            raise ValueError("Only ar and en languages are supported.")

        json = self.requestData(chapter,ayah, lang)
        self.parseResponse(json)

    def requestData(self, chapter, ayah, lang):
        request = requests.get(API_URL, params = {"chapter":chapter,"number":ayah,"lang":lang})
        return request.json()

    def parseResponse(self, json):
        self.verseName = json["ChapterName"]
        self.ayahNumber = json["Id"]
        self.ayahText = json["Text"]



class QuranFinder(callbacks.Plugin):
    """This plugin gets verse and aya number and sends you the ayah using a web API."""

    def __init__(self, irc):
         self.__parent = super(QuranFinder, self)
         self.__parent.__init__(irc)

    def quran(self, irc, msg, args, surah, ayah, lang):
        """<surah> <ayah> <lang>

        returns ayah number <ayah> of surah number <surah> in <lang> language.
        """
        try:
            data = qdata(surah, ayah, lang)
        except ValueError as e:
            irc.error(str(e))
            return
        except IndexError as e:
            irc.error(str(e) + "broken api?")
            return 

        irc.reply(data.verseName + str(data.ayahNumber) + ": " + data.ayahText)

    quran = wrap(quran, ["int", "int", "text"])



Class = QuranFinder


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:	
