#/bin/bash
cd /var/www/147120/stream-data/
/usr/bin/mplayer -noconsolecontrols http://supernova.linux.zxc:8000/KT4AZ.ogg -ao pcm:nowaveheader:file=./audio-pipe > /dev/null 2>&1 &
/bin/cat ./audio-pipe | /usr/local/bin/slice -b 2646000 > /dev/null 2>&1 &
exit 0

