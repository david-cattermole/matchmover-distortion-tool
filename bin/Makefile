#

all: clean run

clean: 
	@echo Cleaning...
	-rm -f testFiles/*.txt
	-rm -f testFiles/*.sh 
	-rm -f testFiles/*.nk 
	-rm -f testFiles/*.bat
	-rm -f coverage/*

test: clean
	@echo Testing...
	-coverage -e
	-coverage -x test.py
	-coverage -b -d ./coverage

run:
	@echo Running...
	-python2 mmDistortionConverter.py

tags:
	-ctags -e *.py

