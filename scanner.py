#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main
~~~~

Custom scanning script to convert image scans to OCR'd PDFs.

:copyright: (c) 2019 by Andrew Kail.
:license: MIT, see LICENSE for more details

"""


import pathlib
import subprocess
import shutil
import sys
import tempfile

import click
from loguru import logger

GS_OPTIONS = [
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",
    "-dPDFSETTINGS=/default",
    "-dNOPAUSE",
    "-dQUIET",
    "-dBATCH",
    "-dDetectDuplicateImages",
    "-dCompressFonts=true",
    "-r150",
]


def look_for_required_commands():
    """Check for required shell commands."""
    fail = False
    if not shutil.which("convert"):
        logger.error("ImageMagick command convert is not installed")
        fail = True
    if not shutil.which("tesseract"):
        logger.error("Tesseract is not installed")
        fail = True
    if not shutil.which("scanimage"):
        logger.error("Sane is not installed")
        fail = True
    if not shutil.which("gs"):
        logger.error("Ghostscript is not installed")
        fail = True

    if fail:
        sys.exit(1)


look_for_required_commands()


@click.command()
@click.option("-sd", "--sane-device", help='SANE device scanner "scanimage -L"')
@click.option("-sr", "--sane-resolution", default=150, help="SANE scanning resolution")
@click.option("-sb", "--sane-brightness", default=0, help="SANE scanning brightness")
@click.option("-sc", "--sane-contrast", default=0, help="SANE scanning contrast")
@click.option("-sm", "--sane-mode", default='Color', help="SANE scanning color mode")
@click.option("-p", "--pages", prompt=True, help="Number of pages to scan", type=int)
@click.option(
    "-o",
    "--output-dir", type=click.Path(exists=True), default=".", help="Output directory"
)
@click.option("-no", "--no-ocr", is_flag=True)
@click.argument("filename", nargs=1)
@logger.catch
def main(
    pages,
    output_dir,
    filename,
    sane_device,
    sane_resolution,
    sane_contrast,
    sane_brightness,
    sane_mode,
    no_ocr,
):
    """Project main function."""
    # add pdf to end of filename
    if not filename.endswith('.pdf'):
        filename += ".pdf"

    final_output = pathlib.Path(output_dir) / pathlib.Path(filename)
    if final_output.exists():
        logger.error(
            "Output pdf {final_output} already exists", final_output=final_output
        )
        return

    with tempfile.TemporaryDirectory() as simple_tempdir:
        tempdir = pathlib.Path(simple_tempdir)

        page_list = list()
        pdf_list = list()
        # scan files out to temporary directory
        for page in range(pages):
            tpage = page + 1
            input(f"Press Enter to scan page {tpage}")
            page_name = pathlib.Path(f"page_{page}.tiff")
            page_path = tempdir / page_name
            with open(page_path, "w") as out_page:
                subprocess.run(
                    [
                        "scanimage",
                        "-d",
                        f"{sane_device}",
                        "--resolution",
                        str(sane_resolution),
                        "--brightness",
                        str(sane_brightness),
                        "--contrast",
                        str(sane_contrast),
                        "--mode",
                        str(sane_mode),
                        "--format",
                        "tiff",
                    ],
                    stdout=out_page,
                )
            page_list.append(page_path)
            print("\tDone!")

        # ocr the images using tesseract
        for page in page_list:
            pdf_base = page.with_suffix("")
            pdf_out = page.with_suffix(".pdf")
            if not no_ocr:
                subprocess.run(["tesseract", page, pdf_base, "pdf"])
            else:
                subprocess.run(["convert", page, pdf_out])

            pdf_list.append(pdf_out)

        # combine pdfs using ghostscript if more than one page
        if len(pdf_list) == 1:
            final_pdf = pdf_list[0]
        else:
            final_pdf = tempdir / pathlib.Path("final.pdf")
            gs_commands = ["gs"] + GS_OPTIONS + [f"-sOutputFile={final_pdf}"] + pdf_list
            print(gs_commands)
            subprocess.run(gs_commands)

        # move final file from temp directory to output location
        shutil.copyfile(final_pdf, final_output)


if __name__ == "__main__":
    main(auto_envvar_prefix='SCANNER')
