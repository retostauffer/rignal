


.PHONY: run web
web:
	make run
run:
	php -S localhost:3003 -t webapp


.PHONY: get
get:
	(cd bin && ./signal get)
