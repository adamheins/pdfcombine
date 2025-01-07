# pdfcombine

A simple command line tool for splitting, merging, and rotating PDF files.
There are many tools like it, but this one is mine.

## Install

In the command line, run:
```
pipx install git+https://github.com/adamheins/pdfcombine.git
```

## Usage

The basic idea is that the user can specify any number of input PDFs and
specify which pages to keep or remove from them. The result is then merged and
output as a single file. Each input can optionally be rotated and can inputs
can be repeated. Usage:
```
pdfcombine input1.pdf [--keep range | --remove range] [--angle degrees] \
          [input2.pdf [...]] ... [-o output.pdf]
```

The `range` argument is a page range specified with commas and hyphens like
those in typical printer dialogs.

Examples:
```bash
# merge two PDF files
pdfcombine foo.pdf bar.pdf -o out.pdf

# extract first two pages and fourth page of foo.pdf
pdfcombine foo.pdf --keep 1-2,4 -o out.pdf

# combine first two pages of foo.pdf with all but the first two pages of
# bar.pdf
pdfcombine foo.pdf --keep 1-2 bar.pdf --remove 1-2 -o out.pdf

# rotate the first page of foo.pdf by 90 degrees and add the second page of
# bar.pdf
pdfcombine foo.pdf --keep 1 --angle 90 bar.pdf --keep 2 -o out.pdf
```

## License

MIT
