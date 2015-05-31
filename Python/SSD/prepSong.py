#!/usr/bin/env python

from syllableParser import syllableParser
import midifile
import urllib2, sys

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print "Please provide a .kar karaoke file."
    sys.exit(0)

m=midifile.midifile()
m.load_file(filename)

if not m.karfile:
    print "This is not a karaoke file."
    sys.exit(0)

# get tuples for syllable and word start times
(syls, words) = syllableParser(m.karsyl, m.kartimes)

# figure out which track has notes for the lyrics
minDiff = -1
noteTrack = 0
candidatesForRemoval = []
for i in range(m.ntracks):
    thisTrack = [v for v in m.notes if v[4]==i]
    if (len(thisTrack) > 0):
        candidatesForRemoval.append(i)

        # deal with percussion tracks with lots of "notes"
        if len(thisTrack) < 2*len(syls):
            currentSum = 0
            numberOfSums = len(syls)
            for (s,t) in syls:
                minDistance = -1
                for v in thisTrack:
                    if (minDistance == -1) or abs(t-v[5])<minDistance:
                        minDistance = abs(t-v[5])
                currentSum = currentSum + minDistance*minDistance

            if(minDiff == -1) or (currentSum/numberOfSums < minDiff):
                minDiff = currentSum/numberOfSums
                noteTrack = i

print "note track = "+str(noteTrack)
print [v[5] for v in m.notes if v[4]==noteTrack][0:5]
print [t for (s,t) in syls[0:5]]

## check
tracks2remove = [t for t in candidatesForRemoval if t!=noteTrack and t!=m.kartrack]
m.write_file(filename, "__"+filename, tracks2remove, None)


# get TTS word files with hash to avoid copies
wordHash = {}
for (w,t) in words:
    wordHash[w] = []

url = 'http://translate.google.com/translate_tts?tl=pt&q='
header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
for w in wordHash:
    response = urllib2.urlopen(urllib2.Request(url+w, None, header))
    responseBytes = response.read()
    mp3FilePath = './mp3s/'+w.decode('iso-8859-1')+'.mp3'
    f = open(mp3FilePath, 'wb')
    f.write(responseBytes)
    f.close()

