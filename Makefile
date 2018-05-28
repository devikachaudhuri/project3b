
default: lab3b.py
	echo "Success"
	cp lab3b.py lab3b

clean:
	-rm lab3b lab3b-304597339.tar.gz

dist:
	tar -czf lab3b-304597339.tar.gz Makefile lab3b.py README
