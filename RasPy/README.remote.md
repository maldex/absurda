```bash
sudo rm /var/lib/dpkg/info/ddclient.*
sudo dpkg --configure -a
sudo dpkg -r ddclient
sudo dpkg -P ddclient

export confurl="http://-------------/Data/absurda/$(grep Serial /proc/cpuinfo | cut -c23-)"
```

```bash
sudo mkdir /etc/openvpn/.current; sudo chmod 600 /etc/openvpn/.current
sudo apt-get install openvpn -y

sudo bash -c "cat << EOF > /lib/systemd/system/openvpn.service
[Unit]
Description=OpenVPN service
After=network.target

[Service]
ExecStart=/usr/sbin/openvpn /etc/openvpn/.current/now.conf
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF"

sudo wget -O /etc/openvpn/.current/now.conf  "${confurl}-config.ovpn"
sudo wget -O /etc/openvpn/.current/now.creds "${confurl}-config.creds" 

sudo sed -i 's?remote.*?remote openvpn.bnet.gebaschtel.ch 1194 udp4?g' /etc/openvpn/.current/now.conf
sudo sed -i 's?auth-user-pass.*?auth-user-pass /etc/openvpn/.current/now.creds?g' /etc/openvpn/.current/now.conf

sudo bash -c "cat << EOF >> /etc/crontab
# openvpn watchdog  
*/5  *   *   *   *       root     ping -i 60 -c 5 "$(route -n | grep 'tun0' | awk '{print $2;}' | sort -n | tail -n1)" > /dev/null || systemctl restart openvpn | mutt -s 'OpenVPN restarted' log@gebaschtel.ch
EOF"

sudo systemctl daemon-reload
sudo systemctl enable --now openvpn
```

```bash
export DEBIAN_FRONTEND=noninteractive
sudo apt-get -yq install ddclient

sudo sed -i 's/run_daemon=.*/run_daemon=true/g' /etc/default/ddclient

sudo wget -O /etc/ddclient.conf "${confurl}-ddclient.conf" 

sudo systemctl enable --now ddclient
```

```bash
function util_verify_public_resolvability() {
    if ! which dig > /dev/null 2>&1; then
        sudo sudo apt-get install dnsutils
    fi
    if [ "$1" != "" ]; then assumedPublicName=$1; else assumedPublicName=`hostname -f`; fi
    assumedPublicIP=`dig +short +answer ${assumedPublicName} @resolver1.opendns.com  | grep -E '^[0-9.]+$'`
    myPublicIP=`dig +short +answer myip.opendns.com @resolver1.opendns.com`
    myPublicName=`dig +short +answer -x ${myPublicIP} @resolver1.opendns.com`
    echo " actual public addresses:  ${myPublicIP} - ${myPublicName}"
    echo "assumed public addresses:  ${assumedPublicIP} - ${assumedPublicName}"
     
    if [ "${assumedPublicIP}" != "${myPublicIP}" ]; then
        echo >&2 "WARNING: IP does not match hostname, do NOT send mails directly from this host but use a relayhost"
        return 2
        fi
    echo >&2 "mails can directly be sent from this host"
    return 0
}

# setup postfix with assumptions ...
function install_postfix() {
    echo "  >> installing postfix"
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get install -yq postfix mutt
    sudo systemctl stop postfix
    sudo rmdir /etc/postfix/dynamicmaps.cf.d /etc/postfix/postfix-files.d  /etc/postfix/sasl/

    echo "  >> setting up postfix"
    if [ -z "${SENDERDOMAIN}" ]; then SENDERDOMAIN="${myPublicName}"; fi
    if [ -z "${RECEIPIENT}" ]; then RECEIPIENT="log@gebaschtel.ch"; fi
    if [ -z "${RELAYHOST}" ]; then RELAYHOST=""; fi
    echo "  >> will send mails as '${SENDERDOMAIN}' to '${RECEIPIENT}' via '${RELAYHOST}'"
    
    # function to see if SENDERDOMAIN matches to my own public ip address
    util_verify_public_resolvability ${SENDERDOMAIN}
    public_resolvable=$?
    
    echo -n "  >> senderdomain '${SENDERDOMAIN}' resolves to me: "
    if [ "${public_resolvable}" == "0" ]; then
        echo "YES: no need for sender-rewriting"
    else
        echo "NO: rewriting sender and receipient (catch-all to '${RECEIPIENT}')"
    fi
        
    # overwrite postfix configuration
    sudo bash -c 'cat << EOF > /etc/postfix/main.cf
# localhost-only mail-relay
inet_protocols = ipv4
inet_interfaces = loopback-only
mynetworks = 127.0.0.0/8
mailbox_size_limit = 0
allow_percent_hack = no
# rewrite "from" and "subject" fields
header_checks = pcre:/etc/postfix/header_checks.pcre
# rewrite "to" field
#recipient_canonical_maps = regexp:/etc/postfix/recipient.regex
# send mail to smarthost instead directly to recipient
#relayhost = RELAYHOST
# when sending directly (w/o relay host), set myhostname to your public IP/Name 
#myhostname = SENDERDOMAIN
EOF'
    
    sudo bash -c 'cat << EOF > /etc/postfix/header_checks.pcre
### tweak the from-address look
/From:(.*)<(.*)@(.*)>/ REPLACE From: RWT${1}<${2}_AT_${3}@SENDERDOMAIN>
/From:(.*)<(.*)>/ REPLACE From: RWT${1}<${2}@SENDERDOMAIN>
# ${1} = orginal display name
# ${2} = orginal email name
# ${3} = orginal hostname
# ${4} = orginal domainname
EOF'
 
    sudo bash -c 'cat << EOF > /etc/postfix/recipient.regex
### send ALL mail to this address
/./     RECEIPIENT
EOF' 

    # apply values from above
    sudo sed -i "s?RECEIPIENT?"${RECEIPIENT}"?g"       /etc/postfix/*
    sudo sed -i "s?RELAYHOST?"${RELAYHOST}"?g"         /etc/postfix/*
    if [ "${RELAYHOST}" != "" ]; then
        sudo sed -i "s?#relayhost?"${RELAYHOST}"?g"      /etc/postfix/main.cf
        fi
    if [ "${SENDERDOMAIN}" != "" ]; then
        sudo sed -i "s?SENDERDOMAIN?"${SENDERDOMAIN}"?g"   /etc/postfix/*
        fi
    if [ "${MY_ENVIRONMENT}}" != "" ]; then
        sudo sed -i "s?RWT?${MY_ENVIRONMENT}?g"   /etc/postfix/*
        fi
        
    # local unix mail aliases
    if ! grep -q "${RECEIPIENT}" /etc/aliases; then
        sudo bash -c 'echo "root:  ${RECEIPIENT}" >> /etc/aliases'
        sudo sed -i "s?^root:.*?root: "${RECEIPIENT}"?g" /etc/aliases
        sudo newaliases
        fi
     
    # do you want to fetch all generated mail and send to receipient only if public reverse lookup does not match?
    if [ "public_resolvable" != "0" ]; then   # when i go to internet, internet does not resolve back to me - i'll be a spammer :(
        # activate receipient rewriting / catch-all rule
        sudo sed -i "s?#recipient_canonical_maps?recipient_canonical_maps?g"   /etc/postfix/main.cf
        sudo sed -i "s?header_checks?#header_checks?g"   /etc/postfix/main.cf
        fi
    
    sudo chmod g-w /etc/postfix/*
    sudo systemctl restart postfix; systemctl status postfix
    
    # delete all enqueued mails from failing tests before - nasty
    sudo postsuper -d ALL

    echo "this mail was supposed for someone..., maybe got redirected to ${RECEIPIENT}" | mutt -s "just say hi, here is `hostname` `date`" log@gebaschtel.ch
}

install_postfix "rpi-$(grep Serial /proc/cpuinfo | cut -c23-).gebaschtel.ch" "log@gebaschtel.ch" "talkto.gebaschtel.ch"
```