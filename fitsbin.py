import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
from pathlib import Path
import argparse
import os
import logging
from skimage.measure import block_reduce

def binning_fast(arr, binning_arr=(2,2)):
    return block_reduce(arr, block_size=binning_arr, func=np.sum)

def adjust_header(header):
    header['XPIXSZ'] = header['XPIXSZ']*2
    header['YPIXSZ'] = header['YPIXSZ']*2
    header['XBINNING'] = header['XBINNING']*2
    header['YBINNING'] = header['YBINNING']*2

def binned_filename(fits, binning):
    return fits.parent/(fits.stem+f'_{binning}x{binning}'+fits.suffix)

def getWcs(wcs_file):
    hdulist = fits.open(wcs_file)
    data = hdulist[0].data.astype(float)
    header = hdulist[0].header
    wcs = WCS(header)
    return wcs

def run(binning, file):
    fits_file = Path(file)
    wcs = getWcs(fits_file)
    hdulist = fits.open(fits_file)
    data = hdulist[0].data
    data_binned=binning_fast(data, binning_arr=(binning, binning))
    hdulist[0].data = data_binned.astype(np.uint16)
    adjust_header(hdulist[0].header)
    outfile = binned_filename(fits_file, binning)
    print(f"writing {outfile}")
    hdulist.writeto(outfile, overwrite=True)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description='munipack automation cli')
    parser.add_argument('-b', '--binning',
                        help="Binning, e.g -b 2 is 2x2 binning", type=int, required=True)
    parser.add_argument('files', nargs='+', help='Files to process')
    args = parser.parse_args()
    for fits_file in args.files:
        run(int(args.binning), fits_file)


