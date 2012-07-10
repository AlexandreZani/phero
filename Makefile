test:
	python -m unittest test_phero

clean:
	rm -f *.pyc

lint:
	pylint \
		--indent-string="  " \
		--reports=n \
		phero.py
