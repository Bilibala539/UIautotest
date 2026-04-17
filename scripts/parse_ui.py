"""解析 UI 树并输出关键元素"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xml.etree.ElementTree as ET

tree = ET.parse(r'C:\Users\wb.menglingzhao02\Desktop\ui.xml')
root = tree.getroot()

def print_node(node, depth=0):
    text = node.attrib.get('text', '')
    content_desc = node.attrib.get('content-desc', '')
    resource_id = node.attrib.get('resource-id', '')
    clz = node.attrib.get('class', '')
    bounds = node.attrib.get('bounds', '')
    clickable = node.attrib.get('clickable', 'false')
    
    short_clz = clz.split(".")[-1] if "." in clz else clz
    short_id = resource_id.split("/")[-1] if "/" in resource_id else resource_id
    
    if text or content_desc or (resource_id and 'com.netease.popo' in resource_id):
        indent = '  ' * depth
        info = f'{indent}[{short_clz}] bounds={bounds}'
        if short_id:
            info += f' id={short_id}'
        if text:
            info += f' text="{text}"'
        if content_desc:
            info += f' desc="{content_desc}"'
        if clickable == 'true':
            info += ' CLICK'
        print(info)
    
    for child in node:
        print_node(child, depth + 1)

print_node(root)
