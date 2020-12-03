import sys
import os
import html as Html
from bs4 import BeautifulSoup
import unicodedata

class parameter:
    def __init__(self,name,class_type):
        self.name = name
        self.class_type = class_type
        self.javadoc = ""

    def __str__(self):
        return str(self.class_type)+" "+str(self.name)
    def __repr__(self):
        return self.__str__()

class method_info:
    def __init__(self,signature,returns,parameters,throws,is_constructor,description):
        self.signature = signature
        self.parameters = parameters
        self.returns = returns
        self.description = description
        self.is_constructor = is_constructor
        self.throws = throws

    def __str__(self):
        return str(self.signature) + "(" + str(self.parameters) + ")" + " throws:" + str(self.throws)
    def __repr__(self):
        return self.__str__()

class class_info:
    def __init__(self,class_name,c_type,class_module,href,path):
        self.c_type = c_type
        self.name = class_name 
        self.module = class_module
        self.href = href
        self.path = path
        self.implements = []
        self.extends = None
        self.methods = []
        self.description = None 

    def __str__(self):
        return str(self.c_type) +" " + str(self.name)
    def __repr__(self):
        return self.__str__()

def loadHtml(filepath):
    with open(filepath) as f:
        lines = ""
        for line in f.readlines():
            lines += line
        return lines

def get_class_infos(root_path,soup):
    links = soup.find_all("a")

    infos = []
    for a in links:
        
        # get basic data

        name = a.text.strip()
        href = a["href"]
        path = get_path_from_href(root_path,"",href)
        title =  a["title"].split("in uk",1)
        module = "uk"+title[-1].strip()
        c_type = title[0].strip()
        info = class_info(name,c_type,module,href,path)

        # get detail info

        load_class_detail(info,root_path)

        infos.append(info)
    return infos 

def load_class_detail(info,root_path):
    html = loadHtml(info.path)
    html_soup = BeautifulSoup(html,"html.parser")

    description = html_soup.select("div[class='description']")[0]
    details = html_soup.select("div[class='details']")[0]
    description_text = description.text

    class_description_div = description.find("div")

    if class_description_div is not None:
        info.description = class_description_div.text.strip()


    # if enum don't fill in anything
    if info.c_type == "enum":
        return
    # get extends information
    if "extends" in description_text:
        extends_a = description.find("pre").select("a")[0]
        info.extends = extends_a.text
    
    # get implemented interafaces 
    if "All Implemented Interfaces:" in description_text:
        code_tags = description.find("dd").find_all("code")
        implemented_as = []
        for c in code_tags:
            implemented_as.append(c.find("a"))
        info.implements = [x.text.strip() for x in implemented_as]

    # get method data
    regions = details.find_all("section")
    constructor_region = None
    method_region = None

    for r in regions:
        for h3s in r.find_all("h3"):
            if h3s.text.strip() == "Constructor Detail":
                constructor_region = r
            elif h3s.text.strip() == "Method Detail":
                method_region = r

    for region in [constructor_region,method_region]:
        if region is not None:
            method_list = [ul.find("li") for ul in region.find("ul").find_all("ul")]
            for m in method_list:
                info.methods.append(get_method_info(m))

def get_method_info(method_section):
    #name of constructors is always the same

    # description
    javadoc_block = method_section.find("div")
    javadoc = javadoc_block.text.strip() if javadoc_block is not None else ""

    # parameters
    
    # first find descriptions
    parameter_detail_list = method_section.find("dl")
    parameter_descriptions = []
    returns_description = None
    throws_descriptions = []
    param_ret_throws = parameter_detail_list.findChildren(recursive=False) if parameter_detail_list is not None else []
    
    last_dt = None
    for d in param_ret_throws:
        if d.name == "dt":
            last_dt = d.text.strip()
            continue
        else: 
            if last_dt == "Parameters:":
                parameter_descriptions.append(d)
            elif last_dt == "Returns:":
                returns_description = d
            elif last_dt == "Throws:":
                throws_descriptions.append(d)

    # then signatured parameters
    method_call = unicodedata.normalize("NFKD",method_section.find("pre").text.strip())
    method_call_split= method_call.split("(")

    constructor = False
    
    signature_items = method_call_split[0]
    
    if len(signature_items.split(" ")) <= 2:
        constructor = True
    
    signature = signature_items

    inside_bracket_signature = method_call_split[1].split(")")[0].strip()
    
    parameters = []
    if inside_bracket_signature is not "":
        parameter_signatures = inside_bracket_signature.split(",\n")

        for p in parameter_signatures:
            splitp = p.strip().split(" ")
            ptype = splitp[0]
            pname = splitp[1]
            parameters.append(parameter(pname,ptype))
    
    # reconcile parameters with descriptions
    # sometimes we don't have desriptions
    if len(parameter_descriptions) == len(parameters):
        for p,pd in zip(parameters,parameter_descriptions):
            p.javadoc = "".join(pd.text.strip().split("-")[1:])

    method = method_info(
        signature,
        returns_description.text.strip().split(":")[0].strip() if returns_description is not None else "",
        parameters,
        [x.text.strip() if x is not None else "" for x in throws_descriptions],
        constructor,
        javadoc)
    return method

def get_path_from_href(root_path,curr_href,href):
    return os.path.join(root_path,curr_href,href)


def parse_jdoc(site):

    all_classes_filename = "allclasses.html"

    class_summary_html = loadHtml(os.path.join(site,all_classes_filename))
    soup_classes = BeautifulSoup(class_summary_html,"html.parser")

    classes = get_class_infos(site,soup_classes)

    return classes




