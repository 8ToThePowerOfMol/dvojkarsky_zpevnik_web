import os
import re
import shutil


def get_songs_in_songbook_old():
    songbook_name = os.path.join("..", "..", "DvojkarskyZpevnik", "Cely_zpevnik", "Zpevnik.tex")
    if os.path.isfile(songbook_name):
        with open(songbook_name, "r", encoding="UTF-8") as f:
            content = list(filter(lambda x: re.search("\\\importsong\{.*\}\{.*\}", x), f.readlines()))
        return {x.split("{")[1].split("}")[0]: x.split("{")[2].split("}")[0] for x in content}
    return {}


def _cleanlatex(raw):
    cleantext = re.sub(re.compile("\\\[^\^\& ]*"), '', raw)
    cleantext = re.sub(re.compile("%%.*"), '', cleantext)
    cleantext = cleantext.replace(" }", " ")
    return cleantext


def get_songname_from_texfile(file):
    with open(file, "r") as f:
        for line in f.readlines():
            if "title=" in line:
                content = line
                break
    songname = _cleanlatex(content.split("\\\\")[0])
    songauthor = _cleanlatex(content.split("\\\\")[1]) if "\\\\" in content else ""
    ret = "{} ({})".format(songname, songauthor)
    ret = re.sub(re.compile("\(\s*"), "(", ret)
    ret = re.sub(re.compile("\s*\)"), ")", ret)
    ret = ret.replace(" ()", "")
    ret = re.sub(re.compile("\s*$"), "", ret)
    return ret


def get_songs_in_songbook():
    songs_dir = os.path.join("..", "..", "DvojkarskyZpevnik", "songy")
    songs = os.listdir(songs_dir)
    songs = list(filter(lambda x: not x.startswith("0") and not x.startswith("ZZ") and x.endswith(".tex"), songs))
    songs.sort()
    return {get_songname_from_texfile(os.path.join(songs_dir, x)): x for x in songs}


def _clean_songs(songs_id, tex_path):
    for f in list(filter(lambda x: songs_id in x, os.listdir(tex_path))):
        os.remove(os.path.join(tex_path, f))


def produce_songs_pdf(songs_dict):
    files_to_typeset = [x for (x, y) in filter(lambda x: x[1], songs_dict)]
    tex_dir = os.path.join("..", "..", "DvojkarskyZpevnik", "web")

    # Lazy loading -- if we made given songlist before, just return its pdf
    songs_id = str(hash(str(files_to_typeset)))
    result_path = os.path.join(tex_dir, "pdfs", songs_id + ".pdf")
    if songs_id + ".pdf" in os.listdir(os.path.join(tex_dir, "pdfs")):
        return result_path, None

    # Prepare .tex file with songs
    songsfile = os.path.join(tex_dir, songs_id + "songs.tex")
    with open(songsfile, "w", encoding="UTF-8") as f:
        for x in files_to_typeset:
            f.write("\\input{../songy/" + x + "}\\newpage\n")

    # Copy generator file with linking to songfile
    genfile = os.path.join(tex_dir, songs_id + ".tex")
    with open(os.path.join(tex_dir, "generator.tex"), "r") as f:
        content = f.readlines()
        content[186] = "\\input{" + songs_id + "songs.tex}\n"
    with open(genfile, "w") as f:
        f.writelines(content)

    # Typeset song
    os.system("TEXINPUTS=.:{}/:{}/:$TEXINPUTS pdflatex -synctex=1 -interaction=batchmode -output-directory {}/ {}".format(
        os.path.abspath(tex_dir), os.path.join("..", "..", "DvojkarskyZpevnik"), tex_dir, genfile))
    pdffile = os.path.join(tex_dir, songs_id + ".pdf")
    if not os.path.isfile(pdffile):
        logfile = os.path.join(tex_dir, songs_id + ".log")
        content = None
        if os.path.isfile(logfile):
            with open(os.path.join(logfile), "r") as f:
                content = f.readlines()
        _clean_songs(songs_id, tex_dir)
        return None, content
    shutil.copy2(pdffile, result_path)
    _clean_songs(songs_id, tex_dir)

    return result_path, None
