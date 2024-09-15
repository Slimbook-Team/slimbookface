get-po:
	pygettext3 -d slimbookface -o locale/messages.pot src/slimbookface.py

locales: locale/es.mo

locale/%.mo:
	mkdir -p locale/mos/$*/LC_MESSAGES
	msgfmt locale/$*.po -o locale/mos/$*/LC_MESSAGES/slimbookface.mo

all: locales

clean:
	rm -rf locale/mos
