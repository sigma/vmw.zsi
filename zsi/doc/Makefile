# $Header$

# put the path to where the Python source was untar'd here (not where it
# is installed)
PYSRCDIR=	
MKHOWTO=	$(PYSRCDIR)/Doc/tools/mkhowto
#PAPER=		a4
PAPER=		letter

CHAPTERS=	c01-intro.tex c02-samples.tex \
		c03-except.tex c04-utils.tex c05-parse.tex c06-tc.tex \
		c07-writer.tex c08-fault.tex c09-resolve.tex \
		c10-dispatch.tex c11-wsdl.tex

M=		zsi

SOURCES=	$M.tex version.tex $(CHAPTERS) zsixsd.tex


all:	ps pdf html
pdf:	$M.pdf
ps:	$M.ps
html:	$M.html
.PHONY: all pdf ps html

$M.ps: $(SOURCES)
	$(MKHOWTO) --dvi $M.tex
	dvips -N0 -t $(PAPER) -o $@ $M.dvi
	@rm $M.dvi
$M.pdf: $(SOURCES)
	$(MKHOWTO) --pdf $M.tex
$M.html: $(SOURCES)
	$(MKHOWTO) --html --split=1 $M.tex
	mv $M/$M.html $M/$M.css .
	rm -rf $M zsi.l2h

zsixsd.tex: zsi.xsd
	sed -e '1,/-->/d' zsi.xsd | expand >$@
version.tex: ../setup.cfg
	( cd .. && make doc/version.tex )

clean:
	rm -f *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn *.pla *.how
clobber: clean
	rm -f $M.ps $M.pdf $M.html $M.l2h $M.css zsixsd.tex
realclean: clobber
distclean: clobber
.PHONY: clean clobber realclean distclean
