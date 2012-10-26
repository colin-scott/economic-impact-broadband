all:
		pdflatex paper-proposal.tex
		pdflatex paper-proposal.tex
		bibtex paper-proposal.aux
		pdflatex paper-proposal.tex
