# use
# python3 parser.py config.yaml "report_v/report.tex"
# python3 parser.py config.yaml "report_x/report.tex"
# to run script with test files

import TexSoup
import yaml
import PyPDF2

import sys
import os


section_indexes = list()
section_names = list()
expected_section_names = list()
section_container: TexSoup.TexNode


def get_sections(tex_tree):
    count = 0
    global section_container
    for node in tex_tree:
        if isinstance(node, TexSoup.TexNode):
            if node.name == "section":
                section_indexes.append(count)
                section_names.append(str(node.args)[1:-1])

                section_container = node.parent
            else:
                get_sections(node)
        count += 1


def check_number_of_sections(expected_names, actual_names):
    l_expected = len(expected_names)
    l_actual = len(actual_names)

    if l_expected != l_actual:
        print(u'\u2717', " Wrong number of section, expected ", 
        l_expected, "but got ", l_actual)

        return 1
    else:
        print(u'\u2713', "OK")
        return 0


def check_section_order():
    all_correct = True
    for i, section in enumerate(section_names):
        if i > len(expected_section_names)-1:
            print(u'\u2717', " Didn't expect section [", 
            section, "] here")
            continue
        if section != expected_section_names[i]:
            print(u'\u2717', " Wrong section, expected [", 
            expected_section_names[i], "] but got [", section, "]")

            all_correct = False

    if all_correct:
        print(u'\u2713', "OK")
        return 0
    else:
        return 1


def non_empty():
    emptyness_map = list()

    for i, index in enumerate(section_indexes):
        count = 0
        emptyness_map.append(False)
        section_begin = index

        if i == len(section_indexes)-1:
            section_end = sys.maxsize
        else:
            section_end = section_indexes[i+1]

        for node in section_container:
            if count == section_end:
                break
            elif count > section_begin:
                if (isinstance(node, TexSoup.utils.TokenWithPosition) and
                    not str(node).startswith('%')):
                    s = str(node).strip()
                    if s != "":
                        emptyness_map[i] = True
                        break
                elif isinstance(node, TexSoup.TexNode):
                    emptyness_map[i] = True
                    break
            count += 1
    
    return emptyness_map


def check_text_content(section_index, expected_content):
    section_begin = section_indexes[section_index]
    section_end = section_indexes[section_index+1]

    actual_content = ""
    count = 0
    
    for node in section_container:
        if count == section_end:
            break
        elif count > section_begin:
            if (isinstance(node, TexSoup.utils.TokenWithPosition) and
            not str(node).startswith('%')):
                actual_content += str(node).strip()
        count += 1

    if actual_content == expected_content.strip():
        print(u'\u2713', " Section [", section_names[section_index], "] text")
        return 0
    else:
        print(u'\u2717', " Wrong section content, \nexpected:\n", 
            expected_content, "\nbut got:\n", actual_content)
        return 1


def check_img_content(section_index, number_of_images):
    section_begin = section_indexes[section_index]
    section_end = section_indexes[section_index+1]

    imgs_actual = 0
    count = 0
    
    for node in section_container:
        if count == section_end:
            break
        elif count > section_begin and isinstance(node, TexSoup.TexNode):
            imgs_actual += node.count("includegraphics")
        count += 1

    if number_of_images == imgs_actual:
        print(u'\u2713', " Section [", section_names[section_index], "] images")
        return 0
    else:
        print(u'\u2717', " Wrong number of images, expected:", 
            number_of_images, "but got:", imgs_actual)
        
        return 1


def check_code_content(section_index):
    section_begin = section_indexes[section_index]
    if section_index == len(section_indexes)-1:
        section_end = sys.maxsize
    else:
        section_end = section_indexes[section_index+1]

    listing_found = False
    count = 0
    
    for node in section_container:
        if count == section_end:
            break
        elif count > section_begin and isinstance(node, TexSoup.TexNode):
            if (node.name == "lstinputlisting" or 
                node.name == "lstlisting" or
                node.name == "lstdefinestyle"):
                listing_found = True
                break
        count += 1

    if listing_found:
        print(u'\u2713', " Section [", section_names[section_index], "] code")
        return 0
    else:
        print(u'\u2717', " Didn't found code listing in [", 
        section_names[section_index], "]")

        return 1


def get_expected_section_names(settings):
    for section in settings["sections"]:
        if isinstance(section, dict):
            for k in section.keys():
                expected_section_names.append(k)
        else:
            expected_section_names.append(section)


def run_content_tests(settings):
    err = 0

    count = 0
    for section in settings["sections"]:
        # there is content to search in section
        if isinstance(section, dict):
            for content in section.values():
                # if there is more than one content to search
                if isinstance(content, dict):
                    for item, value in content.items():
                        err = pick_content_test(count, item, value)
                # only one content to search
                else:
                    err = pick_content_test(count, content[0])
        count += 1

    return err


def pick_content_test(section_index, c_type, content=None):
    if c_type == "text":
        return check_text_content(section_index, content)
    elif c_type == "img":
        return check_img_content(section_index, content)
    elif c_type == "code":
        return check_code_content(section_index)


def check_pages(settings, pdf_file):
    expected_pages = settings["pages"]
    actual_pages = pdf_file.getNumPages()

    if actual_pages >= expected_pages:
        print(u'\u2713', "OK")
        return 0
    else:
        print(u'\u2717', " Wrong number of pages, expected minimum:", 
            expected_pages, "but got:", actual_pages)
        
        return 1


def main(config, rep):
    if not config.endswith('.yaml'):
        print("wrong config file")
        return 1
    elif not rep.endswith('.tex'):
        print("wrong report file")
        return 1

    # os.system("pdflatex main.tex")
    
    tex_file = open(rep)
    soup = TexSoup.TexSoup(tex_file)

    yml_file = open(config)
    settings = yaml.load(yml_file, Loader=yaml.FullLoader)

    pre, _ = os.path.splitext(rep)
    pdf_path = pre + ".pdf"

    pdf_file = PyPDF2.PdfFileReader(pdf_path)

    get_sections(soup)
    get_expected_section_names(settings)

    err = 0
    
    print("> Checking number of sections...")
    err += check_number_of_sections(expected_section_names, section_names)
    
    print("> Checking number of pages...")
    err += check_pages(settings, pdf_file)   

    print("> Checking section names...")
    err += check_section_order()

    print("> Checking if sections is empty...")
    ne_map = non_empty()

    if False in ne_map:
        for section, status in zip(section_names, ne_map):
            if status == False:
                err += 1
                print(u'\u2717', "Section [", section, "] has no contents")
    else:
        print(u'\u2713', "OK")

    print("> Checking specific section contents")
    err += run_content_tests(settings)

    print(err)
    if err > 0:
        return 1
    return 0


# Run program as main file
if __name__ == '__main__':
    config = sys.argv[1]
    rep = sys.argv[2]

    main(config, rep)

