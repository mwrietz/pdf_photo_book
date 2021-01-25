#/usr/bin/env python3

# pdf_photo_book.py

# todo
# o give options for portrait or landscape

import os
import sys
import pathlib
import subprocess
from shutil import copyfile
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

def main():
    arg_count = len(sys.argv)
    if arg_count != 2:
        print('usage: python3 pdf_photo_book.py photodirectory\n')
        quit()

    photopath  = pathlib.Path(sys.path[0]) / sys.argv[1] 
    outputpath = photopath / 'photos_reduced_50pct'
    outputpath.mkdir()
    print(f'\ncreating: {outputpath}\n')

    filelist = list(photopath.glob('*.jpg')) + list(photopath.glob('*.JPG')) + list(photopath.glob('*.jpeg'))
    filelist.sort()

    index = 0
    print('processing:\n')
    for filepath in filelist:
        index += 1
        ofile = outputpath / filepath.name
        print(f'{index} of {len(filelist)}: {get_camera(filepath)} - {filepath.name}')
        cmd = f'convert {str(filepath)}  -resize 50\% -quality 75 {str(ofile)}'
        print(f'    --> convert  : {str(filepath)}')
        subprocess.run(['convert', f'{str(filepath)}', '-resize', '50%', '-quality', '75', f'{str(ofile)}'])
        write_md(ofile)
        create_pdf(ofile)

    combine_pdfs(outputpath)

def write_md(filepath):
    print(f'    --> writing  : {filepath.stem}.md')
    os.chdir(filepath.parent)
    with open(f'{filepath.stem}.md', 'w') as f:
        f.write('---\n')
        f.write('geometry: \"landscape,left=0cm,right=0cm,top=4cm,bottom=4cm\"\n')
        f.write('\n')
        f.write('header-includes:\n')
        f.write('- \\usepackage{caption}\n')
        f.write('- \\usepackage{color}\n')
        f.write('- \\DeclareCaptionFont{myColor}{\color[RGB]{169,169,169}}\n')
        f.write('- \\captionsetup[figure]{labelformat=empty,textfont=myColor}\n')
        f.write('---\n')
        f.write('\n')
        f.write('\\pagenumbering{gobble}\n')
        f.write('\n')
        cam = get_camera(filepath)
        dt = get_date_taken(filepath)
        caption = filepath.name + '   -|-   ' + dt + '   -|-   ' + cam 
        buffer = f'![{caption}]({filepath.name})' + '{ width=100% }\n' 
        f.write(buffer)
    return

def create_pdf(filepath):
    print(f'    --> creating : {filepath.stem}.pdf\n')
    os.chdir(filepath.parent)
    subprocess.run(['pandoc', f'{filepath.stem}.md', '-s', '-o', f'{filepath.stem}.pdf'])
    return

def combine_pdfs(filepath):
    os.chdir(filepath)
    filelist = list(filepath.glob('*.pdf'))
    filelist.sort()
    if len(filelist) > 1:
        firstfile = filelist[0]
        del filelist[0:1]
        photobookfile = filepath / 'photobook.pdf'
        newfile = filepath / 'newfile.pdf'
        copyfile(firstfile, photobookfile)
        print(f'combining pdfs --> {photobookfile}\n')
        for file in filelist:
            subprocess.run(['pdftk', f'{photobookfile}', f'{file}', 'cat', 'output', f'{newfile}'])
            copyfile(newfile, photobookfile)
            newfile.unlink()
        print(f'created: {photobookfile}')
    return

def get_field (exif, field): 
  for (k,v) in exif.items():
     if TAGS.get(k) == field:
        return v

def get_camera(img_path):
    img = Image.open(img_path)
    exif = img._getexif()
    make = get_field(exif, 'Make')
    model = get_field(exif, 'Model')
    camera = make + ' ' + model
    return camera

def get_date_taken(img_path):
    img = Image.open(img_path)
    exif = img._getexif()
    date_taken = get_field(exif, 'DateTimeOriginal')
    return date_taken 

if __name__ == '__main__':
    main()
