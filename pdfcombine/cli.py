#!/usr/bin/env python3
"""Flexibly combine (parts of) PDF files."""
from collections import deque
import os
import sys

import colorama
from pypdf import PdfReader, PdfWriter


USAGE = """Flexibly combine (parts of) PDF files.

Usage:
    pdfcombine input1.pdf [--keep range | --remove range] [--angle degrees] \\
              [input2.pdf [...]] ... [-o output.pdf]

Examples:
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
""".strip()


class Operation:
    """An operation to perform on a PDF file.

    Includes pages to keep or remove, and rotation.

    Parameters
    ----------
    filename : str
        The name of the file.
    page_range : str or None
        The range of pages to keep or remove.
    keep : bool
        True means keep (only) the specified pages. False means remove the
        specified pages (leaving all others).
    angle : int
        The angle to rotate the pages, in degrees.
    """

    def __init__(self, filename, page_range=None, keep=True, angle=0):
        self.filename = filename
        self.page_range = page_range
        self.keep = keep

        # angle to rotate, in degrees
        self.angle = angle

    def __repr__(self):
        return f"Operation(filename={self.filename}, page_range={self.page_range}, keep={self.keep})"

    def pages_to_keep(self, N):
        """The set of pages of the PDF to keep."""
        all_pages = set(range(N))
        if self.page_range is None:
            return all_pages

        pages = parse_page_range(self.page_range)
        if self.keep:
            return pages
        return all_pages - pages


def highlight(s):
    """Color a string yellow."""
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


def parse_page_range(s, zero_index=True):
    """Convert a string representing a page range to a set of pages."""
    pages = set()
    ranges = s.split(",")
    for r in ranges:
        limits = r.split("-")
        if len(limits) == 1:
            pages.add(int(limits[0]))
        elif len(limits) == 2:
            low = int(limits[0])
            high = int(limits[1])
            if high < low:
                raise ValueError(f"invalid range: {r}")
            pages.update(range(low, high + 1))
        else:
            raise ValueError(f"failed to parse page range: {s}")

    if zero_index:
        pages = set([p - 1 for p in pages])
    return pages


def parse_output_file(args):
    """Parse the output file out of the argument list."""
    try:
        idx_o = args.index("-o")
    except ValueError:
        idx_o = -1

    try:
        idx_output = args.index("--output")
    except ValueError:
        idx_output = -1

    if idx_o > 0 and idx_output > 0:
        raise ValueError("Both -o and --output specified. Aborting.")

    idx = max(idx_o, idx_output)
    if idx == -1:
        return "combined.pdf"
    outfile = args.pop(idx + 1)
    args.pop(idx)
    return outfile


def main():
    colorama.init()
    args_to_process = sys.argv[1:].copy()

    if (
        len(args_to_process) == 0
        or "-h" in args_to_process
        or "--help" in args_to_process
    ):
        print(USAGE)
        return

    # parse combined output file name
    try:
        outfile = parse_output_file(args_to_process)
    except ValueError as e:
        print(e)
        return
    if os.path.exists(outfile):
        print(f"Output file {highlight(outfile)} already exists. Aborting.")
        return

    # parse operations to perform
    # TODO should do more checking here
    args_to_process = deque(args_to_process)
    operations = []
    while len(args_to_process) > 0:
        last_file = args_to_process.popleft()
        if not os.path.isfile(last_file):
            print(f"File {highlight(last_file)} does not exist. Aborting.")
            return

        operation = Operation(filename=last_file)
        while len(args_to_process) > 0 and args_to_process[0].startswith("-"):
            cmd = args_to_process.popleft()
            value = args_to_process.popleft()

            if cmd == "-k" or cmd == "--keep":
                operation.keep = True
                operation.page_range = value
            elif cmd == "-r" or cmd == "--remove":
                operation.keep = False
                operation.page_range = value
            elif cmd == "-a" or cmd == "--angle":
                operation.angle = int(value)
            else:
                print(f"Error: failed to parse argument: {highlight(current)}")
                return

        operations.append(operation)

    # combine the PDFs
    writer = PdfWriter()
    for op in operations:
        reader = PdfReader(op.filename)
        try:
            pages_to_keep = op.pages_to_keep(len(reader.pages))
        except ValueError as e:
            print(f"error: {e}")
            return

        # add all pages to the writer
        for i in pages_to_keep:
            writer.add_page(reader.pages[i])

            # rotate the page if required
            if op.angle != 0:
                writer.pages[-1].rotate(op.angle)

    with open(outfile, "wb") as fp:
        writer.write(fp)
    print(f"Saved combined PDF to {highlight(outfile)}.")


if __name__ == "__main__":
    main()
