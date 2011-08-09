all:

clean:
	find ./ -iname "*~" -exec $(RM) {} \;
	find ./ -iname "*.pyc" -exec $(RM) {} \;
