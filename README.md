# javadoc-class-extractor
Extracts all class information from javadoc and outputs it as a nice list of python classes


# requirements
run `pip install`

# usage

```python
from extract_classes.py import parse_jdoc

path_to_site = "" # your path to the site folder containing the all_classes.html file
classes = parse_jdoc(site_path)

# get a class name 
classes[0].name

# find its methods 
classes[0].methods[0].parameters

# get descriptions
classes[0]
```


# class parameters
extract from the script:
```python
class parameter:
    def __init__(self,name,class_type):
        self.name = name
        self.class_type = class_type
        self.javadoc = ""
class method_info:
    def __init__(self,signature,returns,parameters,throws,is_constructor,description):
        self.signature = signature
        self.parameters = parameters
        self.returns = returns
        self.description = description
        self.is_constructor = is_constructor
        self.throws = throws

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
```

# additional goodies
example of mapping classes to latex files can be found in *classes_to_tex.py*
run using `python classes-to-tex.py <path to site folder containing allclasses.index>`
This will create a doc.tex file which is to be inserted into your document with \input,
it will also create a paste-me-directly.tex file which is to be copied into the pre-amble of your latex file
