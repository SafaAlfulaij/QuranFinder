Quran Finder
============

Limnoria/Supybot plugin that brings verses from Quran using a website API

It was developed by a member of ##islam channel in freenode.net IRC network.

How to Use:

```
!quran <surah> <ayah> <lang>
```
returns ayah number <ayah> of surah number <surah> in <lang> language.

```
!quran 1 1 en
```
Returns 
```
1,1: Praise be to Allah, Lord of the Worlds,
```

The bot can obtain translation of the Quran for different languages. (ar, en, fa, tr) are the main ones. You can get extra translations and other data sources by using the data source key provided by Global Quran API. For more information see the [Wiki](https://github.com/SafaAlfulaij/QuranFinder/wiki)

One example is:
```
!quran 1 1 en.hilali
```
which will provide the Hilali English translation of the Quran.

## License
This program is free software under GNU General Public License 3 or any later version and COMES WITHOUT AND WARRANTY, for more information see LICENSE.

## To-Do
- [ ] Don't send a message for each ayah and split messages, instead use supybot's more
