#!/bin/bash

if test "$1" = "disable"; then
	sed -i '/howdy/ c#auth    [success=2 default=ignore]        pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/common-auth
	if grep -q  howdy "/etc/pam.d/sudo"; then
		sed -i '/howdy/ cauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/sudo
	else
		sed -i '/%PAM-1.0/ c#%PAM-1.0\nauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/sudo
	fi
	if grep -q  howdy "/etc/pam.d/polkit-1"; then
		sed -i '/howdy/ cauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/polkit-1
	else
		sed -i '/%PAM-1.0/ c#%PAM-1.0\nauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/polkit-1
	fi
elif test "$1" = "enable"; then
	sed -i '/howdy/ cauth    [success=2 default=ignore]        pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/common-auth
	if grep -q  howdy "/etc/pam.d/sudo"; then
		sed -i '/howdy/ c#auth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/sudo
	else
		sed -i '/%PAM-1.0/ c#%PAM-1.0\n#auth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/sudo		
	fi
	if grep -q  howdy "/etc/pam.d/polkit-1"; then
		sed -i '/howdy/ c#auth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/polkit-1
	else
		sed -i '/%PAM-1.0/ c#%PAM-1.0\n#auth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/polkit-1
	fi
else
	sed -i '/howdy/ c#auth    [success=2 default=ignore]        pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/common-auth
	if grep -q  howdy "/etc/pam.d/sudo"; then
		sed -i '/howdy/ cauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/sudo
	else
		sed -i '/%PAM-1.0/ c#%PAM-1.0\nauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/sudo		
	fi
	if grep -q  howdy "/etc/pam.d/polkit-1"; then
		sed -i '/howdy/ cauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/polkit-1
	else
		sed -i '/%PAM-1.0/ c#%PAM-1.0\nauth    sufficient pam_python.so /lib/security/howdy/pam.py' /etc/pam.d/polkit-1
	fi
	reboot
fi
