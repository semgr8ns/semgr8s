#!/bin/sh
set -euo pipefail

# Update packages
#apk update --no-cache && apk upgrade --no-cache && rm -rf /var/cache/apk

# Remove apk
find / -type f -iname '*apk*' -xdev -delete
find / -type d -iname '*apk*' -print0 -xdev | xargs -0 rm -r --

# Remove pip
pip uninstall pip --yes

# Remove user accounts
echo "" >/etc/group
echo "" >/etc/passwd
echo "" >/etc/shadow

# Remove crons
rm -fr /var/spool/cron
rm -fr /etc/crontabs
rm -fr /etc/periodic

# Remove init scripts
rm -fr /etc/init.d
rm -fr /etc/conf.d
rm -f /etc/inittab

# Remove media stuff
rm -f /etc/fstab
rm -fr /media

# Remove this file
rm "$0"
