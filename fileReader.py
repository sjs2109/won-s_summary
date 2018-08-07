
import sys
import pdfminer.settings
pdfminer.settings.STRICT = False
import pdfminer.high_level
import pdfminer.layout
from pdfminer.image import ImageWriter
import os
from konlpy.tag import Hannanum
import re
import collections

from wordcloud import WordCloud
import matplotlib.pyplot as plt


def extract_text(files=[], outfile='-',
            _py2_no_more_posargs=None,  # Bloody Python2 needs a shim
            no_laparams=False, all_texts=None, detect_vertical=None, # LAParams
            word_margin=None, char_margin=None, line_margin=None, boxes_flow=None, # LAParams
            output_type='text', codec='utf-8', strip_control=False,
            maxpages=0, page_numbers=None, password="", scale=1.0, rotation=0,
            layoutmode='normal', output_dir=None, debug=False,
            disable_caching=False, **other):
    if _py2_no_more_posargs is not None:
        raise ValueError("Too many positional arguments passed.")
    if not files:
        raise ValueError("Must provide files to work upon!")

    # If any LAParams group arguments were passed, create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        for param in ("all_texts", "detect_vertical", "word_margin", "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    imagewriter = None
    if output_dir:
        imagewriter = ImageWriter(output_dir)

    if output_type == "text" and outfile != "-":
        for override, alttype in (  (".htm", "html"),
                                    (".html", "html"),
                                    (".xml", "xml"),
                                    (".tag", "tag") ):
            if outfile.endswith(override):
                output_type = alttype

    if outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            codec = 'utf-8'
    else:
        outfp = open(outfile, "wb")


    for fname in files:
        with open(fname, "rb") as fp:
            pdfminer.high_level.extract_text_to_fp(fp, **locals())
    return outfp


def search(dirname):
    filelist = []
    try:
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            if os.path.isdir(full_filename):
                search(full_filename)
            else:
                ext = os.path.splitext(full_filename)[-1]
                if ext == '.pdf':
                    filelist.append(full_filename)
    except PermissionError:
        pass

    return filelist

def draw_word_cloud(list,name):
    # convert list to string and generate
    unique_string = (" ").join(list)

    wordcloud = WordCloud(font_path="C:\Windows\Fonts\malgun.ttf", width=1000, height=500).generate(unique_string)
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(name+".png")
    plt.show()
    plt.close()

def main(args=None):

    print("Loading pdf files...")
    try:
        os.remove("temp.txt")
        os.remove("Korean.png")
        os.remove("English.png")
    except PermissionError:
        pass
    outfp = extract_text(files= search("./sample_pdf") , outfile="temp.txt")
    outfp.close()

    print("Loading data...")
    f= open("temp.txt", encoding='UTF8')
    elements = f.readlines()
    elements = [x for x in elements if x != "\n"]
    elements = [x.rstrip() for x in elements]

    hannanum = Hannanum()
    korean_list = []
    korean_noun_list = []
    english_list = []

    korean = re.compile('[^ ㄱ-ㅣ가-힣]+')

    for element in elements:
        korean_list.append(korean.sub("",element))

    korean_list = [x.strip() for x in korean_list]
    korean_list = [x for x in korean_list if x != '']

    print("Parsing Korean words...")
    for korean in korean_list:
        korean_noun_list += hannanum.nouns(korean)

    print("Korean list : ",korean_noun_list)

    print("Parsing English words...")
    for element in elements:
        english_list.append(re.sub('[^a-zA-Z]','',element))

    english_list = [x.strip() for x in english_list]
    english_list = [x for x in english_list if x != '']
    print("English list : ", english_list)

    korean_counter = collections.Counter(korean_noun_list)
    print("Most 10 word in Korean words:", korean_counter.most_common(10))

    english_counter = collections.Counter(english_list)
    print("Most 10 word in English words:", english_counter.most_common(10))

    draw_word_cloud(korean_noun_list,"Korean")
    draw_word_cloud(english_list,"English")
    print("Done")

if __name__ == '__main__': sys.exit(main())
