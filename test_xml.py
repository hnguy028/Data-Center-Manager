import xml.etree.ElementTree as ET

xml_file = """<item>
  <a1>value1</a1>
  <a2>value2</a2>
  <a3>value3</a3>
  <a4>
    <a11>value222</a11>
    <a22>value22</a22>
  </a4>
</item>"""

if __name__ == "__main__":
    root = ET.fromstringlist(xml_file)
    node = root[3]
    for i in node:
        print(i.text)
