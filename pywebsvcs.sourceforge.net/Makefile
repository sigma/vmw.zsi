                                                                                
all:    build_zsi_docs
 
build_zsi_docs:
	( cd ../zsi/doc && make all )
	cp ../zsi/doc/zsi.html . 
 
clean:
	rm -rf zsi.html
 
install:
	rsync -rlt * -e ssh blunck2@shell.sourceforge.net:/home/groups/p/py/pywebsvcs/htdocs

