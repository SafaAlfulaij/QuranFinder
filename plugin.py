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

API_URL = "http://api.globalquran.com/ayah/" #verse:ayah/quranID
# Set languages and translations the bot will accept
quranID = {"ar" : "quran-simple", "en" : "en.sahih", "tr" : "tr.yazir", "fa" : "fa.fooladvand"}

TOKEN = "the token" # Token obtained from http://docs.globalquran.com

import requests

class qdata():
    def __init__(self, chapter, ayah, lang):
        if(lang == None):
            lang = "en"
        if(len(lang) == 2):
            if(lang not in quranID):
                raise ValueError("Only " + " ,".join(quranID) + " languages are supported using two letters code. Maybe you would like to use a translation/tafsir code instead, Check: https://git.io/vwMz4 for a list of avalible sources.")
            lang = quranID[lang]

        if (chapter > 114 or chapter < 1):
            raise ValueError("Invalid Surah number.")

        json = self.requestData(chapter, ayah, lang)
        self.parseResponse(json)

        if (int(self.SurahNumber) != chapter): # If the ayah number is bigger
        # than the ayahs in the surah, the API jumps to another surah.
            raise ValueError("Invalid Ayah number.")

    def requestData(self, chapter, ayah, lang):
        url = API_URL + str(chapter) + ":" + str(ayah) + "/" + lang
        request = requests.get(url, params = {'key' : TOKEN})
        json = request.json()

        # the ID differs for each verse. So there is no static key to call in the main json.
        for quran in json:
            json = json[quran]
            for quranVer in json: # the QuranID in the json. Here we used quranVar to avoid conflict with the quranID above.
                json = json[quranVer]
                for ID in json:
                    json = json[ID]

        return json

    def parseResponse(self, json):
        self.SurahNumber = json["surah"]
        self.ayahNumber = json["ayah"]
        self.ayahText = json["verse"]
class utilities():
    def arg2list(ayat): # TODO: better name for this function
        try:
            return [int(ayat)]
        except ValueError:
            t = ayat.split('-') 
            start, end = int(t[0]), int(t[1])
            if (end - start) not in range(1, 6):
                raise ValueError("Out of range(max is 5) or start ayah is" +
                "bigger than end ayah.") #TODO: a better message please
            else:
                return list(range(start, end + 1))
            


class QuranFinder(callbacks.Plugin):
    """This plugin gets verse and ayah number and sends you the ayah using a web API."""

    def __init__(self, irc):
         self.__parent = super(QuranFinder, self)
         self.__parent.__init__(irc)

    def quran(self, irc, msg, args, surah, ayat, lang):
        """<surah> <ayah/ayat> <lang>

        returns ayah number <ayah> of surah number <surah> in <lang> language or translation or tafsir. for more information visit: https://git.io/vwMz9
        """
        
        try:
            list_of_ayat = utilities.arg2list(ayat)
        except ValueError as e:
            irc.error(str(e))

        try:
            ayat_str = ''
            for ayah in list_of_ayat:
                data = qdata(surah, ayah, lang)
                ayat_str += str(data.SurahNumber)
                ayat_str += str(data.ayahNumber)
                ayat_str += str(data.ayahText)
                ayat_str += '\n'
        except ValueError as e:
            irc.error(str(e))
            return
        except (KeyError, TypeError) as e: #TypeError incase requesting a audio version. The json would contain a list so qdata would raise a TypeError
            irc.error("Wrong translation code or broken API.") 
            return
        
        for ayah in ayat_str.split('\n'):

            if self.registryValue('splitMessages'):
                ircMsgBytes = (ayah).encode('utf-8')
                while len(ircMsgBytes) > 350:
                    splitPoint = ircMsgBytes[0:351].rfind(' '.encode('utf-8'))
                    irc.reply(ircMsgBytes[0:splitPoint].decode('utf-8').strip())
                    ircMsgBytes = ircMsgBytes[splitPoint:]
                irc.reply(ircMsgBytes.decode('utf-8').strip())
            else:
                irc.reply(ayah)

    quran = wrap(quran, ["int", "something", optional("something")])




Class = QuranFinder


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
