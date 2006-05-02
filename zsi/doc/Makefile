# $Header$

# put the path to where the Python source was untar'd here (not where it
# is installed)
PYSRCDIR=	/usr/lib/python2.4
MKHOWTO=	PATH=$$PATH:$(PYSRCDIR)/doc/tools mkhowto
#PAPER=		a4
PAPER=		letter

M_CHAPTERS=	c01-intro.tex c02-samples.tex \
		c03-except.tex c04-utils.tex c05-parse.tex c06-tc.tex \
		c07-writer.tex c08-fault.tex c09-resolve.tex \
		c10-dispatch.tex c11-wsdl.tex
	
G_CHAPTERS = 

M=		zsi
G=		zsi-ug

SOURCES=	$M.tex $G.tex version.tex $(M_CHAPTERS) $(G_CHAPTERS) zsixsd.tex


all:	ps pdf html
pdf:	$M.pdf $G.pdf
ps:		$M.ps $G.ps
html:	$M.html $G.html
.PHONY: all pdf ps html

$M.ps: $(SOURCES)
	$(MKHOWTO) --dvi $M.tex
	dvips -N0 -t $(PAPER) -o $@ $M.dvi
	rm $M.dvi

$G.ps: $(SOURCES)
	$(MKHOWTO) --dvi $G.tex
	dvips -N0 -t $(PAPER) -o $@ $G.dvi
	rm $G.dvi

$M.pdf: $(SOURCES)
	$(MKHOWTO) --pdf $M.tex

$G.pdf: $(SOURCES)
	$(MKHOWTO) --pdf $G.tex

$M.html: $(SOURCES)
	$(MKHOWTO) --html --split=1 $M.tex
	mv $M/$M.html $M/$M.css .
	rm -rf $M zsi.l2h

$G.html: $(SOURCES)
	$(MKHOWTO) --html --split=1 $G.tex
	mv $G/$G.html $G/$G.css .
	rm -rf $G zsi.l2h

zsixsd.tex: zsi.xsd
	sed -e '1,/-->/d' zsi.xsd | expand >$@

clean:
	rm -f *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn *.pla *.how
clobber: clean
	rm -f $M.ps $M.pdf $M.html $M.l2h $M.css $G.ps $G.pdf $G.html zsixsd.tex 
realclean: clobber
distclean: clobber
.PHONY: clean clobber realclean distclean
