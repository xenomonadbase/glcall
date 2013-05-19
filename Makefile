

install:
	install -m 755 bin/glcall.py /usr/local/bin/glcall.py
	install -m 644 etc/glcall /etc/bash_completion.d/glcall
	install -m 644 etc/glvim /etc/bash_completion.d/glvim


