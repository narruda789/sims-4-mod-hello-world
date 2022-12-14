# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\dom\minidom.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 68800 bytes
import io, xml.dom
from xml.dom import EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE, domreg
from xml.dom.minicompat import *
from xml.dom.xmlbuilder import DOMImplementationLS, DocumentLS
_nodeTypes_with_children = (
 xml.dom.Node.ELEMENT_NODE,
 xml.dom.Node.ENTITY_REFERENCE_NODE)

class Node(xml.dom.Node):
    namespaceURI = None
    parentNode = None
    ownerDocument = None
    nextSibling = None
    previousSibling = None
    prefix = EMPTY_PREFIX

    def __bool__(self):
        return True

    def toxml(self, encoding=None):
        return self.toprettyxml('', '', encoding)

    def toprettyxml(self, indent='\t', newl='\n', encoding=None):
        if encoding is None:
            writer = io.StringIO()
        else:
            writer = io.TextIOWrapper((io.BytesIO()), encoding=encoding,
              errors='xmlcharrefreplace',
              newline='\n')
        if self.nodeType == Node.DOCUMENT_NODE:
            self.writexml(writer, '', indent, newl, encoding)
        else:
            self.writexml(writer, '', indent, newl)
        if encoding is None:
            return writer.getvalue()
        return writer.detach().getvalue()

    def hasChildNodes(self):
        return bool(self.childNodes)

    def _get_childNodes(self):
        return self.childNodes

    def _get_firstChild(self):
        if self.childNodes:
            return self.childNodes[0]

    def _get_lastChild(self):
        if self.childNodes:
            return self.childNodes[(-1)]

    def insertBefore(self, newChild, refChild):
        if newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            for c in tuple(newChild.childNodes):
                self.insertBefore(c, refChild)

            return newChild
        if newChild.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr('%s cannot be child of %s' % (repr(newChild), repr(self)))
        if newChild.parentNode is not None:
            newChild.parentNode.removeChild(newChild)
        if refChild is None:
            self.appendChild(newChild)
        else:
            try:
                index = self.childNodes.index(refChild)
            except ValueError:
                raise xml.dom.NotFoundErr()

            if newChild.nodeType in _nodeTypes_with_children:
                _clear_id_cache(self)
            else:
                self.childNodes.insert(index, newChild)
                newChild.nextSibling = refChild
                refChild.previousSibling = newChild
                if index:
                    node = self.childNodes[(index - 1)]
                    node.nextSibling = newChild
                    newChild.previousSibling = node
                else:
                    newChild.previousSibling = None
            newChild.parentNode = self
        return newChild

    def appendChild(self, node):
        if node.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            for c in tuple(node.childNodes):
                self.appendChild(c)

            return node
        elif node.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr('%s cannot be child of %s' % (repr(node), repr(self)))
        else:
            if node.nodeType in _nodeTypes_with_children:
                _clear_id_cache(self)
        if node.parentNode is not None:
            node.parentNode.removeChild(node)
        _append_child(self, node)
        node.nextSibling = None
        return node

    def replaceChild(self, newChild, oldChild):
        if newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            refChild = oldChild.nextSibling
            self.removeChild(oldChild)
            return self.insertBefore(newChild, refChild)
            if newChild.nodeType not in self._child_node_types:
                raise xml.dom.HierarchyRequestErr('%s cannot be child of %s' % (repr(newChild), repr(self)))
            if newChild is oldChild:
                return
            if newChild.parentNode is not None:
                newChild.parentNode.removeChild(newChild)
        else:
            try:
                index = self.childNodes.index(oldChild)
            except ValueError:
                raise xml.dom.NotFoundErr()

        self.childNodes[index] = newChild
        newChild.parentNode = self
        oldChild.parentNode = None
        if newChild.nodeType in _nodeTypes_with_children or oldChild.nodeType in _nodeTypes_with_children:
            _clear_id_cache(self)
        newChild.nextSibling = oldChild.nextSibling
        newChild.previousSibling = oldChild.previousSibling
        oldChild.nextSibling = None
        oldChild.previousSibling = None
        if newChild.previousSibling:
            newChild.previousSibling.nextSibling = newChild
        if newChild.nextSibling:
            newChild.nextSibling.previousSibling = newChild
        return oldChild

    def removeChild(self, oldChild):
        try:
            self.childNodes.remove(oldChild)
        except ValueError:
            raise xml.dom.NotFoundErr()

        if oldChild.nextSibling is not None:
            oldChild.nextSibling.previousSibling = oldChild.previousSibling
        if oldChild.previousSibling is not None:
            oldChild.previousSibling.nextSibling = oldChild.nextSibling
        oldChild.nextSibling = oldChild.previousSibling = None
        if oldChild.nodeType in _nodeTypes_with_children:
            _clear_id_cache(self)
        oldChild.parentNode = None
        return oldChild

    def normalize(self):
        L = []
        for child in self.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                if not child.data:
                    if L:
                        L[(-1)].nextSibling = child.nextSibling
                    if child.nextSibling:
                        child.nextSibling.previousSibling = child.previousSibling
                    child.unlink()
                elif L:
                    if L[(-1)].nodeType == child.nodeType:
                        node = L[(-1)]
                        node.data = node.data + child.data
                        node.nextSibling = child.nextSibling
                        if child.nextSibling:
                            child.nextSibling.previousSibling = node
                        child.unlink()
                    else:
                        L.append(child)
                else:
                    L.append(child)
                    if child.nodeType == Node.ELEMENT_NODE:
                        child.normalize()

        self.childNodes[:] = L

    def cloneNode(self, deep):
        return _clone_node(self, deep, self.ownerDocument or self)

    def isSupported(self, feature, version):
        return self.ownerDocument.implementation.hasFeature(feature, version)

    def _get_localName(self):
        pass

    def isSameNode(self, other):
        return self is other

    def getInterface(self, feature):
        if self.isSupported(feature, None):
            return self
        return

    def getUserData(self, key):
        try:
            return self._user_data[key][0]
        except (AttributeError, KeyError):
            return

    def setUserData(self, key, data, handler):
        old = None
        try:
            d = self._user_data
        except AttributeError:
            d = {}
            self._user_data = d

        if key in d:
            old = d[key][0]
        elif data is None:
            handler = None
            if old is not None:
                del d[key]
        else:
            d[key] = (
             data, handler)
        return old

    def _call_user_data_handler(self, operation, src, dst):
        if hasattr(self, '_user_data'):
            for key, (data, handler) in list(self._user_data.items()):
                if handler is not None:
                    handler.handle(operation, key, data, src, dst)

    def unlink(self):
        self.parentNode = self.ownerDocument = None
        if self.childNodes:
            for child in self.childNodes:
                child.unlink()

            self.childNodes = NodeList()
        self.previousSibling = None
        self.nextSibling = None

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        self.unlink()


defproperty(Node, 'firstChild', doc='First child node, or None.')
defproperty(Node, 'lastChild', doc='Last child node, or None.')
defproperty(Node, 'localName', doc='Namespace-local name of this node.')

def _append_child(self, node):
    childNodes = self.childNodes
    if childNodes:
        last = childNodes[(-1)]
        node.previousSibling = last
        last.nextSibling = node
    childNodes.append(node)
    node.parentNode = self


def _in_document(node):
    while node is not None:
        if node.nodeType == Node.DOCUMENT_NODE:
            return True
        node = node.parentNode

    return False


def _write_data(writer, data):
    if data:
        data = data.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;').replace('>', '&gt;')
        writer.write(data)


def _get_elements_by_tagName_helper(parent, name, rc):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            if name == '*' or node.tagName == name:
                rc.append(node)
        _get_elements_by_tagName_helper(node, name, rc)

    return rc


def _get_elements_by_tagName_ns_helper(parent, nsURI, localName, rc):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            if localName == '*' or node.localName == localName:
                if nsURI == '*' or node.namespaceURI == nsURI:
                    rc.append(node)
            _get_elements_by_tagName_ns_helper(node, nsURI, localName, rc)

    return rc


class DocumentFragment(Node):
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = '#document-fragment'
    nodeValue = None
    attributes = None
    parentNode = None
    _child_node_types = (Node.ELEMENT_NODE,
     Node.TEXT_NODE,
     Node.CDATA_SECTION_NODE,
     Node.ENTITY_REFERENCE_NODE,
     Node.PROCESSING_INSTRUCTION_NODE,
     Node.COMMENT_NODE,
     Node.NOTATION_NODE)

    def __init__(self):
        self.childNodes = NodeList()


class Attr(Node):
    __slots__ = ('_name', '_value', 'namespaceURI', '_prefix', 'childNodes', '_localName',
                 'ownerDocument', 'ownerElement')
    nodeType = Node.ATTRIBUTE_NODE
    attributes = None
    specified = False
    _is_id = False
    _child_node_types = (
     Node.TEXT_NODE, Node.ENTITY_REFERENCE_NODE)

    def __init__(self, qName, namespaceURI=EMPTY_NAMESPACE, localName=None, prefix=None):
        self.ownerElement = None
        self._name = qName
        self.namespaceURI = namespaceURI
        self._prefix = prefix
        self.childNodes = NodeList()
        self.childNodes.append(Text())

    def _get_localName(self):
        try:
            return self._localName
        except AttributeError:
            return self.nodeName.split(':', 1)[(-1)]

    def _get_specified(self):
        return self.specified

    def _get_name(self):
        return self._name

    def _set_name(self, value):
        self._name = value
        if self.ownerElement is not None:
            _clear_id_cache(self.ownerElement)

    nodeName = name = property(_get_name, _set_name)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value
        self.childNodes[0].data = value
        if self.ownerElement is not None:
            _clear_id_cache(self.ownerElement)
        self.childNodes[0].data = value

    nodeValue = value = property(_get_value, _set_value)

    def _get_prefix(self):
        return self._prefix

    def _set_prefix(self, prefix):
        nsuri = self.namespaceURI
        if prefix == 'xmlns':
            if nsuri:
                if nsuri != XMLNS_NAMESPACE:
                    raise xml.dom.NamespaceErr("illegal use of 'xmlns' prefix for the wrong namespace")
        else:
            self._prefix = prefix
            if prefix is None:
                newName = self.localName
            else:
                newName = '%s:%s' % (prefix, self.localName)
        if self.ownerElement:
            _clear_id_cache(self.ownerElement)
        self.name = newName

    prefix = property(_get_prefix, _set_prefix)

    def unlink(self):
        elem = self.ownerElement
        if elem is not None:
            del elem._attrs[self.nodeName]
            del elem._attrsNS[(self.namespaceURI, self.localName)]
            if self._is_id:
                self._is_id = False
                elem._magic_id_nodes -= 1
                self.ownerDocument._magic_id_count -= 1
        for child in self.childNodes:
            child.unlink()

        del self.childNodes[:]

    def _get_isId(self):
        if self._is_id:
            return True
        doc = self.ownerDocument
        elem = self.ownerElement
        if doc is None or elem is None:
            return False
        info = doc._get_elem_info(elem)
        if info is None:
            return False
        if self.namespaceURI:
            return info.isIdNS(self.namespaceURI, self.localName)
        return info.isId(self.nodeName)

    def _get_schemaType(self):
        doc = self.ownerDocument
        elem = self.ownerElement
        if doc is None or elem is None:
            return _no_type
        info = doc._get_elem_info(elem)
        if info is None:
            return _no_type
        if self.namespaceURI:
            return info.getAttributeTypeNS(self.namespaceURI, self.localName)
        return info.getAttributeType(self.nodeName)


defproperty(Attr, 'isId', doc='True if this attribute is an ID.')
defproperty(Attr, 'localName', doc='Namespace-local name of this attribute.')
defproperty(Attr, 'schemaType', doc='Schema type for this attribute.')

class NamedNodeMap(object):
    __slots__ = ('_attrs', '_attrsNS', '_ownerElement')

    def __init__(self, attrs, attrsNS, ownerElement):
        self._attrs = attrs
        self._attrsNS = attrsNS
        self._ownerElement = ownerElement

    def _get_length(self):
        return len(self._attrs)

    def item(self, index):
        try:
            return self[list(self._attrs.keys())[index]]
        except IndexError:
            return

    def items(self):
        L = []
        for node in self._attrs.values():
            L.append((node.nodeName, node.value))

        return L

    def itemsNS(self):
        L = []
        for node in self._attrs.values():
            L.append(((node.namespaceURI, node.localName), node.value))

        return L

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self._attrs
        return key in self._attrsNS

    def keys(self):
        return self._attrs.keys()

    def keysNS(self):
        return self._attrsNS.keys()

    def values(self):
        return self._attrs.values()

    def get(self, name, value=None):
        return self._attrs.get(name, value)

    __len__ = _get_length

    def _cmp(self, other):
        if self._attrs is getattr(other, '_attrs', None):
            return 0
        return (id(self) > id(other)) - (id(self) < id(other))

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __getitem__(self, attname_or_tuple):
        if isinstance(attname_or_tuple, tuple):
            return self._attrsNS[attname_or_tuple]
        return self._attrs[attname_or_tuple]

    def __setitem__(self, attname, value):
        if isinstance(value, str):
            try:
                node = self._attrs[attname]
            except KeyError:
                node = Attr(attname)
                node.ownerDocument = self._ownerElement.ownerDocument
                self.setNamedItem(node)

            node.value = value
        else:
            if not isinstance(value, Attr):
                raise TypeError('value must be a string or Attr object')
            node = value
            self.setNamedItem(node)

    def getNamedItem(self, name):
        try:
            return self._attrs[name]
        except KeyError:
            return

    def getNamedItemNS(self, namespaceURI, localName):
        try:
            return self._attrsNS[(namespaceURI, localName)]
        except KeyError:
            return

    def removeNamedItem(self, name):
        n = self.getNamedItem(name)
        if n is not None:
            _clear_id_cache(self._ownerElement)
            del self._attrs[n.nodeName]
            del self._attrsNS[(n.namespaceURI, n.localName)]
            if hasattr(n, 'ownerElement'):
                n.ownerElement = None
            return n
        raise xml.dom.NotFoundErr()

    def removeNamedItemNS(self, namespaceURI, localName):
        n = self.getNamedItemNS(namespaceURI, localName)
        if n is not None:
            _clear_id_cache(self._ownerElement)
            del self._attrsNS[(n.namespaceURI, n.localName)]
            del self._attrs[n.nodeName]
            if hasattr(n, 'ownerElement'):
                n.ownerElement = None
            return n
        raise xml.dom.NotFoundErr()

    def setNamedItem(self, node):
        if not isinstance(node, Attr):
            raise xml.dom.HierarchyRequestErr('%s cannot be child of %s' % (repr(node), repr(self)))
        old = self._attrs.get(node.name)
        if old:
            old.unlink()
        self._attrs[node.name] = node
        self._attrsNS[(node.namespaceURI, node.localName)] = node
        node.ownerElement = self._ownerElement
        _clear_id_cache(node.ownerElement)
        return old

    def setNamedItemNS(self, node):
        return self.setNamedItem(node)

    def __delitem__(self, attname_or_tuple):
        node = self[attname_or_tuple]
        _clear_id_cache(node.ownerElement)
        node.unlink()

    def __getstate__(self):
        return (
         self._attrs, self._attrsNS, self._ownerElement)

    def __setstate__(self, state):
        self._attrs, self._attrsNS, self._ownerElement = state


defproperty(NamedNodeMap, 'length', doc='Number of nodes in the NamedNodeMap.')
AttributeList = NamedNodeMap

class TypeInfo(object):
    __slots__ = ('namespace', 'name')

    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def __repr__(self):
        if self.namespace:
            return '<%s %r (from %r)>' % (self.__class__.__name__, self.name,
             self.namespace)
        return '<%s %r>' % (self.__class__.__name__, self.name)

    def _get_name(self):
        return self.name

    def _get_namespace(self):
        return self.namespace


_no_type = TypeInfo(None, None)

class Element(Node):
    __slots__ = ('ownerDocument', 'parentNode', 'tagName', 'nodeName', 'prefix', 'namespaceURI',
                 '_localName', 'childNodes', '_attrs', '_attrsNS', 'nextSibling',
                 'previousSibling')
    nodeType = Node.ELEMENT_NODE
    nodeValue = None
    schemaType = _no_type
    _magic_id_nodes = 0
    _child_node_types = (
     Node.ELEMENT_NODE,
     Node.PROCESSING_INSTRUCTION_NODE,
     Node.COMMENT_NODE,
     Node.TEXT_NODE,
     Node.CDATA_SECTION_NODE,
     Node.ENTITY_REFERENCE_NODE)

    def __init__(self, tagName, namespaceURI=EMPTY_NAMESPACE, prefix=None, localName=None):
        self.parentNode = None
        self.tagName = self.nodeName = tagName
        self.prefix = prefix
        self.namespaceURI = namespaceURI
        self.childNodes = NodeList()
        self.nextSibling = self.previousSibling = None
        self._attrs = None
        self._attrsNS = None

    def _ensure_attributes(self):
        if self._attrs is None:
            self._attrs = {}
            self._attrsNS = {}

    def _get_localName(self):
        try:
            return self._localName
        except AttributeError:
            return self.tagName.split(':', 1)[(-1)]

    def _get_tagName(self):
        return self.tagName

    def unlink(self):
        if self._attrs is not None:
            for attr in list(self._attrs.values()):
                attr.unlink()

        self._attrs = None
        self._attrsNS = None
        Node.unlink(self)

    def getAttribute(self, attname):
        if self._attrs is None:
            return ''
        try:
            return self._attrs[attname].value
        except KeyError:
            return ''

    def getAttributeNS(self, namespaceURI, localName):
        if self._attrsNS is None:
            return ''
        try:
            return self._attrsNS[(namespaceURI, localName)].value
        except KeyError:
            return ''

    def setAttribute(self, attname, value):
        attr = self.getAttributeNode(attname)
        if attr is None:
            attr = Attr(attname)
            attr.value = value
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        else:
            if value != attr.value:
                attr.value = value
                if attr.isId:
                    _clear_id_cache(self)

    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        prefix, localname = _nssplit(qualifiedName)
        attr = self.getAttributeNodeNS(namespaceURI, localname)
        if attr is None:
            attr = Attr(qualifiedName, namespaceURI, localname, prefix)
            attr.value = value
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        else:
            if value != attr.value:
                attr.value = value
                if attr.isId:
                    _clear_id_cache(self)
            if attr.prefix != prefix:
                attr.prefix = prefix
                attr.nodeName = qualifiedName

    def getAttributeNode(self, attrname):
        if self._attrs is None:
            return
        return self._attrs.get(attrname)

    def getAttributeNodeNS(self, namespaceURI, localName):
        if self._attrsNS is None:
            return
        return self._attrsNS.get((namespaceURI, localName))

    def setAttributeNode(self, attr):
        if attr.ownerElement not in (None, self):
            raise xml.dom.InuseAttributeErr('attribute node already owned')
        else:
            self._ensure_attributes()
            old1 = self._attrs.get(attr.name, None)
            if old1 is not None:
                self.removeAttributeNode(old1)
            old2 = self._attrsNS.get((attr.namespaceURI, attr.localName), None)
            if old2 is not None and old2 is not old1:
                self.removeAttributeNode(old2)
        _set_attribute_node(self, attr)
        if old1 is not attr:
            return old1
        if old2 is not attr:
            return old2

    setAttributeNodeNS = setAttributeNode

    def removeAttribute(self, name):
        if self._attrsNS is None:
            raise xml.dom.NotFoundErr()
        try:
            attr = self._attrs[name]
        except KeyError:
            raise xml.dom.NotFoundErr()

        self.removeAttributeNode(attr)

    def removeAttributeNS(self, namespaceURI, localName):
        if self._attrsNS is None:
            raise xml.dom.NotFoundErr()
        try:
            attr = self._attrsNS[(namespaceURI, localName)]
        except KeyError:
            raise xml.dom.NotFoundErr()

        self.removeAttributeNode(attr)

    def removeAttributeNode(self, node):
        if node is None:
            raise xml.dom.NotFoundErr()
        try:
            self._attrs[node.name]
        except KeyError:
            raise xml.dom.NotFoundErr()

        _clear_id_cache(self)
        node.unlink()
        node.ownerDocument = self.ownerDocument

    removeAttributeNodeNS = removeAttributeNode

    def hasAttribute(self, name):
        if self._attrs is None:
            return False
        return name in self._attrs

    def hasAttributeNS(self, namespaceURI, localName):
        if self._attrsNS is None:
            return False
        return (
         namespaceURI, localName) in self._attrsNS

    def getElementsByTagName(self, name):
        return _get_elements_by_tagName_helper(self, name, NodeList())

    def getElementsByTagNameNS(self, namespaceURI, localName):
        return _get_elements_by_tagName_ns_helper(self, namespaceURI, localName, NodeList())

    def __repr__(self):
        return '<DOM Element: %s at %#x>' % (self.tagName, id(self))

    def writexml(self, writer, indent='', addindent='', newl=''):
        writer.write(indent + '<' + self.tagName)
        attrs = self._get_attributes()
        a_names = sorted(attrs.keys())
        for a_name in a_names:
            writer.write(' %s="' % a_name)
            _write_data(writer, attrs[a_name].value)
            writer.write('"')

        if self.childNodes:
            writer.write('>')
            if len(self.childNodes) == 1 and self.childNodes[0].nodeType == Node.TEXT_NODE:
                self.childNodes[0].writexml(writer, '', '', '')
            else:
                writer.write(newl)
                for node in self.childNodes:
                    node.writexml(writer, indent + addindent, addindent, newl)

                writer.write(indent)
            writer.write('</%s>%s' % (self.tagName, newl))
        else:
            writer.write('/>%s' % newl)

    def _get_attributes(self):
        self._ensure_attributes()
        return NamedNodeMap(self._attrs, self._attrsNS, self)

    def hasAttributes(self):
        if self._attrs:
            return True
        return False

    def setIdAttribute(self, name):
        idAttr = self.getAttributeNode(name)
        self.setIdAttributeNode(idAttr)

    def setIdAttributeNS(self, namespaceURI, localName):
        idAttr = self.getAttributeNodeNS(namespaceURI, localName)
        self.setIdAttributeNode(idAttr)

    def setIdAttributeNode(self, idAttr):
        if not idAttr is None:
            raise self.isSameNode(idAttr.ownerElement) or xml.dom.NotFoundErr()
        else:
            if _get_containing_entref(self) is not None:
                raise xml.dom.NoModificationAllowedErr()
            idAttr._is_id = idAttr._is_id or True
            self._magic_id_nodes += 1
            self.ownerDocument._magic_id_count += 1
            _clear_id_cache(self)


defproperty(Element, 'attributes', doc='NamedNodeMap of attributes on the element.')
defproperty(Element, 'localName', doc='Namespace-local name of this element.')

def _set_attribute_node(element, attr):
    _clear_id_cache(element)
    element._ensure_attributes()
    element._attrs[attr.name] = attr
    element._attrsNS[(attr.namespaceURI, attr.localName)] = attr
    attr.ownerElement = element


class Childless:
    __slots__ = ()
    attributes = None
    childNodes = EmptyNodeList()
    firstChild = None
    lastChild = None

    def _get_firstChild(self):
        pass

    def _get_lastChild(self):
        pass

    def appendChild(self, node):
        raise xml.dom.HierarchyRequestErr(self.nodeName + ' nodes cannot have children')

    def hasChildNodes(self):
        return False

    def insertBefore(self, newChild, refChild):
        raise xml.dom.HierarchyRequestErr(self.nodeName + ' nodes do not have children')

    def removeChild(self, oldChild):
        raise xml.dom.NotFoundErr(self.nodeName + ' nodes do not have children')

    def normalize(self):
        pass

    def replaceChild(self, newChild, oldChild):
        raise xml.dom.HierarchyRequestErr(self.nodeName + ' nodes do not have children')


class ProcessingInstruction(Childless, Node):
    nodeType = Node.PROCESSING_INSTRUCTION_NODE
    __slots__ = ('target', 'data')

    def __init__(self, target, data):
        self.target = target
        self.data = data

    def _get_nodeValue(self):
        return self.data

    def _set_nodeValue(self, value):
        self.data = value

    nodeValue = property(_get_nodeValue, _set_nodeValue)

    def _get_nodeName(self):
        return self.target

    def _set_nodeName(self, value):
        self.target = value

    nodeName = property(_get_nodeName, _set_nodeName)

    def writexml(self, writer, indent='', addindent='', newl=''):
        writer.write('%s<?%s %s?>%s' % (indent, self.target, self.data, newl))


class CharacterData(Childless, Node):
    __slots__ = ('_data', 'ownerDocument', 'parentNode', 'previousSibling', 'nextSibling')

    def __init__(self):
        self.ownerDocument = self.parentNode = None
        self.previousSibling = self.nextSibling = None
        self._data = ''
        Node.__init__(self)

    def _get_length(self):
        return len(self.data)

    __len__ = _get_length

    def _get_data(self):
        return self._data

    def _set_data(self, data):
        self._data = data

    data = nodeValue = property(_get_data, _set_data)

    def __repr__(self):
        data = self.data
        if len(data) > 10:
            dotdotdot = '...'
        else:
            dotdotdot = ''
        return '<DOM %s node "%r%s">' % (
         self.__class__.__name__, data[0:10], dotdotdot)

    def substringData(self, offset, count):
        if offset < 0:
            raise xml.dom.IndexSizeErr('offset cannot be negative')
        if offset >= len(self.data):
            raise xml.dom.IndexSizeErr('offset cannot be beyond end of data')
        if count < 0:
            raise xml.dom.IndexSizeErr('count cannot be negative')
        return self.data[offset:offset + count]

    def appendData(self, arg):
        self.data = self.data + arg

    def insertData(self, offset, arg):
        if offset < 0:
            raise xml.dom.IndexSizeErr('offset cannot be negative')
        if offset >= len(self.data):
            raise xml.dom.IndexSizeErr('offset cannot be beyond end of data')
        if arg:
            self.data = '%s%s%s' % (
             self.data[:offset], arg, self.data[offset:])

    def deleteData(self, offset, count):
        if offset < 0:
            raise xml.dom.IndexSizeErr('offset cannot be negative')
        if offset >= len(self.data):
            raise xml.dom.IndexSizeErr('offset cannot be beyond end of data')
        if count < 0:
            raise xml.dom.IndexSizeErr('count cannot be negative')
        if count:
            self.data = self.data[:offset] + self.data[offset + count:]

    def replaceData(self, offset, count, arg):
        if offset < 0:
            raise xml.dom.IndexSizeErr('offset cannot be negative')
        if offset >= len(self.data):
            raise xml.dom.IndexSizeErr('offset cannot be beyond end of data')
        if count < 0:
            raise xml.dom.IndexSizeErr('count cannot be negative')
        if count:
            self.data = '%s%s%s' % (
             self.data[:offset], arg, self.data[offset + count:])


defproperty(CharacterData, 'length', doc='Length of the string data.')

class Text(CharacterData):
    __slots__ = ()
    nodeType = Node.TEXT_NODE
    nodeName = '#text'
    attributes = None

    def splitText(self, offset):
        if not offset < 0:
            if offset > len(self.data):
                raise xml.dom.IndexSizeErr('illegal offset value')
            newText = self.__class__()
            newText.data = self.data[offset:]
            newText.ownerDocument = self.ownerDocument
            next = self.nextSibling
            if self.parentNode and self in self.parentNode.childNodes:
                if next is None:
                    self.parentNode.appendChild(newText)
        else:
            self.parentNode.insertBefore(newText, next)
        self.data = self.data[:offset]
        return newText

    def writexml(self, writer, indent='', addindent='', newl=''):
        _write_data(writer, '%s%s%s' % (indent, self.data, newl))

    def _get_wholeText(self):
        L = [
         self.data]
        n = self.previousSibling
        while n is not None:
            if n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.insert(0, n.data)
                n = n.previousSibling
            else:
                break

        n = self.nextSibling
        while n is not None:
            if n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.append(n.data)
                n = n.nextSibling
            else:
                break

        return ''.join(L)

    def replaceWholeText(self, content):
        parent = self.parentNode
        n = self.previousSibling
        while n is not None:
            if n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.previousSibling
                parent.removeChild(n)
                n = next
            else:
                break

        n = self.nextSibling
        if not content:
            parent.removeChild(self)
        while n is not None:
            if n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.nextSibling
                parent.removeChild(n)
                n = next
            else:
                break

        if content:
            self.data = content
            return self
        return

    def _get_isWhitespaceInElementContent(self):
        if self.data.strip():
            return False
        elem = _get_containing_element(self)
        if elem is None:
            return False
        info = self.ownerDocument._get_elem_info(elem)
        if info is None:
            return False
        return info.isElementContent()


defproperty(Text, 'isWhitespaceInElementContent', doc='True iff this text node contains only whitespace and is in element content.')
defproperty(Text, 'wholeText', doc='The text of all logically-adjacent text nodes.')

def _get_containing_element(node):
    c = node.parentNode
    while c is not None:
        if c.nodeType == Node.ELEMENT_NODE:
            return c
        c = c.parentNode


def _get_containing_entref(node):
    c = node.parentNode
    while c is not None:
        if c.nodeType == Node.ENTITY_REFERENCE_NODE:
            return c
        c = c.parentNode


class Comment(CharacterData):
    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'

    def __init__(self, data):
        CharacterData.__init__(self)
        self._data = data

    def writexml(self, writer, indent='', addindent='', newl=''):
        if '--' in self.data:
            raise ValueError("'--' is not allowed in a comment node")
        writer.write('%s<!--%s-->%s' % (indent, self.data, newl))


class CDATASection(Text):
    __slots__ = ()
    nodeType = Node.CDATA_SECTION_NODE
    nodeName = '#cdata-section'

    def writexml(self, writer, indent='', addindent='', newl=''):
        if self.data.find(']]>') >= 0:
            raise ValueError("']]>' not allowed in a CDATA section")
        writer.write('<![CDATA[%s]]>' % self.data)


class ReadOnlySequentialNamedNodeMap(object):
    __slots__ = ('_seq', )

    def __init__(self, seq=()):
        self._seq = seq

    def __len__(self):
        return len(self._seq)

    def _get_length(self):
        return len(self._seq)

    def getNamedItem(self, name):
        for n in self._seq:
            if n.nodeName == name:
                return n

    def getNamedItemNS(self, namespaceURI, localName):
        for n in self._seq:
            if n.namespaceURI == namespaceURI and n.localName == localName:
                return n

    def __getitem__(self, name_or_tuple):
        if isinstance(name_or_tuple, tuple):
            node = (self.getNamedItemNS)(*name_or_tuple)
        else:
            node = self.getNamedItem(name_or_tuple)
        if node is None:
            raise KeyError(name_or_tuple)
        return node

    def item(self, index):
        if index < 0:
            return
        try:
            return self._seq[index]
        except IndexError:
            return

    def removeNamedItem(self, name):
        raise xml.dom.NoModificationAllowedErr('NamedNodeMap instance is read-only')

    def removeNamedItemNS(self, namespaceURI, localName):
        raise xml.dom.NoModificationAllowedErr('NamedNodeMap instance is read-only')

    def setNamedItem(self, node):
        raise xml.dom.NoModificationAllowedErr('NamedNodeMap instance is read-only')

    def setNamedItemNS(self, node):
        raise xml.dom.NoModificationAllowedErr('NamedNodeMap instance is read-only')

    def __getstate__(self):
        return [
         self._seq]

    def __setstate__(self, state):
        self._seq = state[0]


defproperty(ReadOnlySequentialNamedNodeMap, 'length', doc='Number of entries in the NamedNodeMap.')

class Identified:
    __slots__ = ('publicId', 'systemId')

    def _identified_mixin_init(self, publicId, systemId):
        self.publicId = publicId
        self.systemId = systemId

    def _get_publicId(self):
        return self.publicId

    def _get_systemId(self):
        return self.systemId


class DocumentType(Identified, Childless, Node):
    nodeType = Node.DOCUMENT_TYPE_NODE
    nodeValue = None
    name = None
    publicId = None
    systemId = None
    internalSubset = None

    def __init__(self, qualifiedName):
        self.entities = ReadOnlySequentialNamedNodeMap()
        self.notations = ReadOnlySequentialNamedNodeMap()
        if qualifiedName:
            prefix, localname = _nssplit(qualifiedName)
            self.name = localname
        self.nodeName = self.name

    def _get_internalSubset(self):
        return self.internalSubset

    def cloneNode(self, deep):
        if self.ownerDocument is None:
            clone = DocumentType(None)
            clone.name = self.name
            clone.nodeName = self.name
            operation = xml.dom.UserDataHandler.NODE_CLONED
            if deep:
                clone.entities._seq = []
                clone.notations._seq = []
                for n in self.notations._seq:
                    notation = Notation(n.nodeName, n.publicId, n.systemId)
                    clone.notations._seq.append(notation)
                    n._call_user_data_handler(operation, n, notation)

                for e in self.entities._seq:
                    entity = Entity(e.nodeName, e.publicId, e.systemId, e.notationName)
                    entity.actualEncoding = e.actualEncoding
                    entity.encoding = e.encoding
                    entity.version = e.version
                    clone.entities._seq.append(entity)
                    e._call_user_data_handler(operation, n, entity)

            self._call_user_data_handler(operation, self, clone)
            return clone
        return

    def writexml(self, writer, indent='', addindent='', newl=''):
        writer.write('<!DOCTYPE ')
        writer.write(self.name)
        if self.publicId:
            writer.write("%s  PUBLIC '%s'%s  '%s'" % (
             newl, self.publicId, newl, self.systemId))
        else:
            if self.systemId:
                writer.write("%s  SYSTEM '%s'" % (newl, self.systemId))
        if self.internalSubset is not None:
            writer.write(' [')
            writer.write(self.internalSubset)
            writer.write(']')
        writer.write('>' + newl)


class Entity(Identified, Node):
    attributes = None
    nodeType = Node.ENTITY_NODE
    nodeValue = None
    actualEncoding = None
    encoding = None
    version = None

    def __init__(self, name, publicId, systemId, notation):
        self.nodeName = name
        self.notationName = notation
        self.childNodes = NodeList()
        self._identified_mixin_init(publicId, systemId)

    def _get_actualEncoding(self):
        return self.actualEncoding

    def _get_encoding(self):
        return self.encoding

    def _get_version(self):
        return self.version

    def appendChild(self, newChild):
        raise xml.dom.HierarchyRequestErr('cannot append children to an entity node')

    def insertBefore(self, newChild, refChild):
        raise xml.dom.HierarchyRequestErr('cannot insert children below an entity node')

    def removeChild(self, oldChild):
        raise xml.dom.HierarchyRequestErr('cannot remove children from an entity node')

    def replaceChild(self, newChild, oldChild):
        raise xml.dom.HierarchyRequestErr('cannot replace children of an entity node')


class Notation(Identified, Childless, Node):
    nodeType = Node.NOTATION_NODE
    nodeValue = None

    def __init__(self, name, publicId, systemId):
        self.nodeName = name
        self._identified_mixin_init(publicId, systemId)


class DOMImplementation(DOMImplementationLS):
    _features = [
     ('core', '1.0'),
     ('core', '2.0'),
     ('core', None),
     ('xml', '1.0'),
     ('xml', '2.0'),
     ('xml', None),
     ('ls-load', '3.0'),
     ('ls-load', None)]

    def hasFeature(self, feature, version):
        if version == '':
            version = None
        return (
         feature.lower(), version) in self._features

    def createDocument(self, namespaceURI, qualifiedName, doctype):
        if doctype:
            if doctype.parentNode is not None:
                raise xml.dom.WrongDocumentErr('doctype object owned by another DOM tree')
        doc = self._create_document()
        add_root_element = not (namespaceURI is None and qualifiedName is None and doctype is None)
        if not qualifiedName:
            if add_root_element:
                raise xml.dom.InvalidCharacterErr('Element with no name')
        if add_root_element:
            prefix, localname = _nssplit(qualifiedName)
            if prefix == 'xml':
                if namespaceURI != 'http://www.w3.org/XML/1998/namespace':
                    raise xml.dom.NamespaceErr("illegal use of 'xml' prefix")
            if prefix:
                if not namespaceURI:
                    raise xml.dom.NamespaceErr('illegal use of prefix without namespaces')
            element = doc.createElementNS(namespaceURI, qualifiedName)
            if doctype:
                doc.appendChild(doctype)
            doc.appendChild(element)
        if doctype:
            doctype.parentNode = doctype.ownerDocument = doc
        doc.doctype = doctype
        doc.implementation = self
        return doc

    def createDocumentType(self, qualifiedName, publicId, systemId):
        doctype = DocumentType(qualifiedName)
        doctype.publicId = publicId
        doctype.systemId = systemId
        return doctype

    def getInterface(self, feature):
        if self.hasFeature(feature, None):
            return self
        return

    def _create_document(self):
        return Document()


class ElementInfo(object):
    __slots__ = ('tagName', )

    def __init__(self, name):
        self.tagName = name

    def getAttributeType(self, aname):
        return _no_type

    def getAttributeTypeNS(self, namespaceURI, localName):
        return _no_type

    def isElementContent(self):
        return False

    def isEmpty(self):
        return False

    def isId(self, aname):
        return False

    def isIdNS(self, namespaceURI, localName):
        return False

    def __getstate__(self):
        return self.tagName

    def __setstate__(self, state):
        self.tagName = state


def _clear_id_cache(node):
    if node.nodeType == Node.DOCUMENT_NODE:
        node._id_cache.clear()
        node._id_search_stack = None
    else:
        if _in_document(node):
            node.ownerDocument._id_cache.clear()
            node.ownerDocument._id_search_stack = None


class Document(Node, DocumentLS):
    __slots__ = ('_elem_info', 'doctype', '_id_search_stack', 'childNodes', '_id_cache')
    _child_node_types = (
     Node.ELEMENT_NODE, Node.PROCESSING_INSTRUCTION_NODE,
     Node.COMMENT_NODE, Node.DOCUMENT_TYPE_NODE)
    implementation = DOMImplementation()
    nodeType = Node.DOCUMENT_NODE
    nodeName = '#document'
    nodeValue = None
    attributes = None
    parentNode = None
    previousSibling = nextSibling = None
    actualEncoding = None
    encoding = None
    standalone = None
    version = None
    strictErrorChecking = False
    errorHandler = None
    documentURI = None
    _magic_id_count = 0

    def __init__(self):
        self.doctype = None
        self.childNodes = NodeList()
        self._elem_info = {}
        self._id_cache = {}
        self._id_search_stack = None

    def _get_elem_info(self, element):
        if element.namespaceURI:
            key = (
             element.namespaceURI, element.localName)
        else:
            key = element.tagName
        return self._elem_info.get(key)

    def _get_actualEncoding(self):
        return self.actualEncoding

    def _get_doctype(self):
        return self.doctype

    def _get_documentURI(self):
        return self.documentURI

    def _get_encoding(self):
        return self.encoding

    def _get_errorHandler(self):
        return self.errorHandler

    def _get_standalone(self):
        return self.standalone

    def _get_strictErrorChecking(self):
        return self.strictErrorChecking

    def _get_version(self):
        return self.version

    def appendChild(self, node):
        if node.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr('%s cannot be child of %s' % (repr(node), repr(self)))
        else:
            if node.parentNode is not None:
                node.parentNode.removeChild(node)
            if node.nodeType == Node.ELEMENT_NODE and self._get_documentElement():
                raise xml.dom.HierarchyRequestErr('two document elements disallowed')
        return Node.appendChild(self, node)

    def removeChild(self, oldChild):
        try:
            self.childNodes.remove(oldChild)
        except ValueError:
            raise xml.dom.NotFoundErr()

        oldChild.nextSibling = oldChild.previousSibling = None
        oldChild.parentNode = None
        if self.documentElement is oldChild:
            self.documentElement = None
        return oldChild

    def _get_documentElement(self):
        for node in self.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                return node

    def unlink(self):
        if self.doctype is not None:
            self.doctype.unlink()
            self.doctype = None
        Node.unlink(self)

    def cloneNode(self, deep):
        if not deep:
            return
        clone = self.implementation.createDocument(None, None, None)
        clone.encoding = self.encoding
        clone.standalone = self.standalone
        clone.version = self.version
        for n in self.childNodes:
            childclone = _clone_node(n, deep, clone)
            clone.childNodes.append(childclone)
            if childclone.nodeType == Node.DOCUMENT_NODE:
                pass
            elif childclone.nodeType == Node.DOCUMENT_TYPE_NODE:
                clone.doctype = childclone
            childclone.parentNode = clone

        self._call_user_data_handler(xml.dom.UserDataHandler.NODE_CLONED, self, clone)
        return clone

    def createDocumentFragment(self):
        d = DocumentFragment()
        d.ownerDocument = self
        return d

    def createElement(self, tagName):
        e = Element(tagName)
        e.ownerDocument = self
        return e

    def createTextNode(self, data):
        if not isinstance(data, str):
            raise TypeError('node contents must be a string')
        t = Text()
        t.data = data
        t.ownerDocument = self
        return t

    def createCDATASection(self, data):
        if not isinstance(data, str):
            raise TypeError('node contents must be a string')
        c = CDATASection()
        c.data = data
        c.ownerDocument = self
        return c

    def createComment(self, data):
        c = Comment(data)
        c.ownerDocument = self
        return c

    def createProcessingInstruction(self, target, data):
        p = ProcessingInstruction(target, data)
        p.ownerDocument = self
        return p

    def createAttribute(self, qName):
        a = Attr(qName)
        a.ownerDocument = self
        a.value = ''
        return a

    def createElementNS(self, namespaceURI, qualifiedName):
        prefix, localName = _nssplit(qualifiedName)
        e = Element(qualifiedName, namespaceURI, prefix)
        e.ownerDocument = self
        return e

    def createAttributeNS(self, namespaceURI, qualifiedName):
        prefix, localName = _nssplit(qualifiedName)
        a = Attr(qualifiedName, namespaceURI, localName, prefix)
        a.ownerDocument = self
        a.value = ''
        return a

    def _create_entity(self, name, publicId, systemId, notationName):
        e = Entity(name, publicId, systemId, notationName)
        e.ownerDocument = self
        return e

    def _create_notation(self, name, publicId, systemId):
        n = Notation(name, publicId, systemId)
        n.ownerDocument = self
        return n

    def getElementById--- This code section failed: ---

 L.1715         0  LOAD_FAST                'id'
                2  LOAD_FAST                'self'
                4  LOAD_ATTR                _id_cache
                6  COMPARE_OP               in
                8  POP_JUMP_IF_FALSE    20  'to 20'

 L.1716        10  LOAD_FAST                'self'
               12  LOAD_ATTR                _id_cache
               14  LOAD_FAST                'id'
               16  BINARY_SUBSCR    
               18  RETURN_VALUE     
             20_0  COME_FROM             8  '8'

 L.1717        20  LOAD_FAST                'self'
               22  LOAD_ATTR                _elem_info
               24  POP_JUMP_IF_TRUE     36  'to 36'
               26  LOAD_FAST                'self'
               28  LOAD_ATTR                _magic_id_count
               30  POP_JUMP_IF_TRUE     36  'to 36'

 L.1718        32  LOAD_CONST               None
               34  RETURN_VALUE     
             36_0  COME_FROM            30  '30'
             36_1  COME_FROM            24  '24'

 L.1720        36  LOAD_FAST                'self'
               38  LOAD_ATTR                _id_search_stack
               40  STORE_FAST               'stack'

 L.1721        42  LOAD_FAST                'stack'
               44  LOAD_CONST               None
               46  COMPARE_OP               is
               48  POP_JUMP_IF_FALSE    66  'to 66'

 L.1723        50  LOAD_FAST                'self'
               52  LOAD_ATTR                documentElement
               54  BUILD_LIST_1          1 
               56  STORE_FAST               'stack'

 L.1724        58  LOAD_FAST                'stack'
               60  LOAD_FAST                'self'
               62  STORE_ATTR               _id_search_stack
               64  JUMP_FORWARD         74  'to 74'
             66_0  COME_FROM            48  '48'

 L.1725        66  LOAD_FAST                'stack'
               68  POP_JUMP_IF_TRUE     74  'to 74'

 L.1728        70  LOAD_CONST               None
               72  RETURN_VALUE     
             74_0  COME_FROM            68  '68'
             74_1  COME_FROM            64  '64'

 L.1730        74  LOAD_CONST               None
               76  STORE_FAST               'result'

 L.1731     78_80  SETUP_LOOP          398  'to 398'
             82_0  COME_FROM           390  '390'
               82  LOAD_FAST                'stack'
            84_86  POP_JUMP_IF_FALSE   396  'to 396'

 L.1732        88  LOAD_FAST                'stack'
               90  LOAD_METHOD              pop
               92  CALL_METHOD_0         0  '0 positional arguments'
               94  STORE_FAST               'node'

 L.1734        96  LOAD_FAST                'stack'
               98  LOAD_METHOD              extend
              100  LOAD_LISTCOMP            '<code_object <listcomp>>'
              102  LOAD_STR                 'Document.getElementById.<locals>.<listcomp>'
              104  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              106  LOAD_FAST                'node'
              108  LOAD_ATTR                childNodes
              110  GET_ITER         
              112  CALL_FUNCTION_1       1  '1 positional argument'
              114  CALL_METHOD_1         1  '1 positional argument'
              116  POP_TOP          

 L.1737       118  LOAD_FAST                'self'
              120  LOAD_METHOD              _get_elem_info
              122  LOAD_FAST                'node'
              124  CALL_METHOD_1         1  '1 positional argument'
              126  STORE_FAST               'info'

 L.1738       128  LOAD_FAST                'info'
          130_132  POP_JUMP_IF_FALSE   318  'to 318'

 L.1742       134  SETUP_LOOP          384  'to 384'
              136  LOAD_FAST                'node'
              138  LOAD_ATTR                attributes
              140  LOAD_METHOD              values
              142  CALL_METHOD_0         0  '0 positional arguments'
              144  GET_ITER         
            146_0  COME_FROM           308  '308'
            146_1  COME_FROM           268  '268'
              146  FOR_ITER            314  'to 314'
              148  STORE_FAST               'attr'

 L.1743       150  LOAD_FAST                'attr'
              152  LOAD_ATTR                namespaceURI
              154  POP_JUMP_IF_FALSE   210  'to 210'

 L.1744       156  LOAD_FAST                'info'
              158  LOAD_METHOD              isIdNS
              160  LOAD_FAST                'attr'
              162  LOAD_ATTR                namespaceURI
              164  LOAD_FAST                'attr'
              166  LOAD_ATTR                localName
              168  CALL_METHOD_2         2  '2 positional arguments'
              170  POP_JUMP_IF_FALSE   208  'to 208'

 L.1745       172  LOAD_FAST                'node'
              174  LOAD_FAST                'self'
              176  LOAD_ATTR                _id_cache
              178  LOAD_FAST                'attr'
              180  LOAD_ATTR                value
              182  STORE_SUBSCR     

 L.1746       184  LOAD_FAST                'attr'
              186  LOAD_ATTR                value
              188  LOAD_FAST                'id'
              190  COMPARE_OP               ==
              192  POP_JUMP_IF_FALSE   200  'to 200'

 L.1747       194  LOAD_FAST                'node'
              196  STORE_FAST               'result'
              198  JUMP_FORWARD        208  'to 208'
            200_0  COME_FROM           192  '192'

 L.1748       200  LOAD_FAST                'node'
              202  LOAD_ATTR                _magic_id_nodes
              204  POP_JUMP_IF_TRUE    208  'to 208'

 L.1749       206  BREAK_LOOP       
            208_0  COME_FROM           204  '204'
            208_1  COME_FROM           198  '198'
            208_2  COME_FROM           170  '170'
              208  JUMP_BACK           146  'to 146'
            210_0  COME_FROM           154  '154'

 L.1750       210  LOAD_FAST                'info'
              212  LOAD_METHOD              isId
              214  LOAD_FAST                'attr'
              216  LOAD_ATTR                name
              218  CALL_METHOD_1         1  '1 positional argument'
          220_222  POP_JUMP_IF_FALSE   264  'to 264'

 L.1751       224  LOAD_FAST                'node'
              226  LOAD_FAST                'self'
              228  LOAD_ATTR                _id_cache
              230  LOAD_FAST                'attr'
              232  LOAD_ATTR                value
              234  STORE_SUBSCR     

 L.1752       236  LOAD_FAST                'attr'
              238  LOAD_ATTR                value
              240  LOAD_FAST                'id'
              242  COMPARE_OP               ==
              244  POP_JUMP_IF_FALSE   252  'to 252'

 L.1753       246  LOAD_FAST                'node'
              248  STORE_FAST               'result'
              250  JUMP_FORWARD        262  'to 262'
            252_0  COME_FROM           244  '244'

 L.1754       252  LOAD_FAST                'node'
              254  LOAD_ATTR                _magic_id_nodes
          256_258  POP_JUMP_IF_TRUE    312  'to 312'

 L.1755       260  BREAK_LOOP       
            262_0  COME_FROM           250  '250'
              262  JUMP_BACK           146  'to 146'
            264_0  COME_FROM           220  '220'

 L.1756       264  LOAD_FAST                'attr'
              266  LOAD_ATTR                _is_id
              268  POP_JUMP_IF_FALSE   146  'to 146'

 L.1757       270  LOAD_FAST                'node'
              272  LOAD_FAST                'self'
              274  LOAD_ATTR                _id_cache
              276  LOAD_FAST                'attr'
              278  LOAD_ATTR                value
              280  STORE_SUBSCR     

 L.1758       282  LOAD_FAST                'attr'
              284  LOAD_ATTR                value
              286  LOAD_FAST                'id'
              288  COMPARE_OP               ==
          290_292  POP_JUMP_IF_FALSE   300  'to 300'

 L.1759       294  LOAD_FAST                'node'
              296  STORE_FAST               'result'
              298  JUMP_BACK           146  'to 146'
            300_0  COME_FROM           290  '290'

 L.1760       300  LOAD_FAST                'node'
              302  LOAD_ATTR                _magic_id_nodes
              304  LOAD_CONST               1
              306  COMPARE_OP               ==
              308  POP_JUMP_IF_FALSE   146  'to 146'

 L.1761       310  BREAK_LOOP       
            312_0  COME_FROM           256  '256'
              312  JUMP_BACK           146  'to 146'
              314  POP_BLOCK        
              316  JUMP_FORWARD        384  'to 384'
            318_0  COME_FROM           130  '130'

 L.1762       318  LOAD_FAST                'node'
              320  LOAD_ATTR                _magic_id_nodes
          322_324  POP_JUMP_IF_FALSE   384  'to 384'

 L.1763       326  SETUP_LOOP          384  'to 384'
              328  LOAD_FAST                'node'
              330  LOAD_ATTR                attributes
              332  LOAD_METHOD              values
              334  CALL_METHOD_0         0  '0 positional arguments'
              336  GET_ITER         
            338_0  COME_FROM           370  '370'
            338_1  COME_FROM           346  '346'
              338  FOR_ITER            382  'to 382'
              340  STORE_FAST               'attr'

 L.1764       342  LOAD_FAST                'attr'
              344  LOAD_ATTR                _is_id
          346_348  POP_JUMP_IF_FALSE   338  'to 338'

 L.1765       350  LOAD_FAST                'node'
              352  LOAD_FAST                'self'
              354  LOAD_ATTR                _id_cache
              356  LOAD_FAST                'attr'
              358  LOAD_ATTR                value
              360  STORE_SUBSCR     

 L.1766       362  LOAD_FAST                'attr'
              364  LOAD_ATTR                value
              366  LOAD_FAST                'id'
              368  COMPARE_OP               ==
          370_372  POP_JUMP_IF_FALSE   338  'to 338'

 L.1767       374  LOAD_FAST                'node'
              376  STORE_FAST               'result'
          378_380  JUMP_BACK           338  'to 338'
              382  POP_BLOCK        
            384_0  COME_FROM_LOOP      326  '326'
            384_1  COME_FROM           322  '322'
            384_2  COME_FROM           316  '316'
            384_3  COME_FROM_LOOP      134  '134'

 L.1768       384  LOAD_FAST                'result'
              386  LOAD_CONST               None
              388  COMPARE_OP               is-not
              390  POP_JUMP_IF_FALSE    82  'to 82'

 L.1769       392  BREAK_LOOP       
              394  JUMP_BACK            82  'to 82'
            396_0  COME_FROM            84  '84'
              396  POP_BLOCK        
            398_0  COME_FROM_LOOP       78  '78'

 L.1770       398  LOAD_FAST                'result'
              400  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_FORWARD' instruction at offset 316

    def getElementsByTagName(self, name):
        return _get_elements_by_tagName_helper(self, name, NodeList())

    def getElementsByTagNameNS(self, namespaceURI, localName):
        return _get_elements_by_tagName_ns_helper(self, namespaceURI, localName, NodeList())

    def isSupported(self, feature, version):
        return self.implementation.hasFeature(feature, version)

    def importNode(self, node, deep):
        if node.nodeType == Node.DOCUMENT_NODE:
            raise xml.dom.NotSupportedErr('cannot import document nodes')
        else:
            if node.nodeType == Node.DOCUMENT_TYPE_NODE:
                raise xml.dom.NotSupportedErr('cannot import document type nodes')
        return _clone_node(node, deep, self)

    def writexml(self, writer, indent='', addindent='', newl='', encoding=None):
        if encoding is None:
            writer.write('<?xml version="1.0" ?>' + newl)
        else:
            writer.write('<?xml version="1.0" encoding="%s"?>%s' % (
             encoding, newl))
        for node in self.childNodes:
            node.writexml(writer, indent, addindent, newl)

    def renameNode(self, n, namespaceURI, name):
        if n.ownerDocument is not self:
            raise xml.dom.WrongDocumentErr('cannot rename nodes from other documents;\nexpected %s,\nfound %s' % (
             self, n.ownerDocument))
        elif n.nodeType not in (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
            raise xml.dom.NotSupportedErr('renameNode() only applies to element and attribute nodes')
        elif namespaceURI != EMPTY_NAMESPACE:
            if ':' in name:
                prefix, localName = name.split(':', 1)
                if prefix == 'xmlns':
                    if namespaceURI != xml.dom.XMLNS_NAMESPACE:
                        raise xml.dom.NamespaceErr("illegal use of 'xmlns' prefix")
                    else:
                        if name == 'xmlns':
                            if namespaceURI != xml.dom.XMLNS_NAMESPACE:
                                if n.nodeType == Node.ATTRIBUTE_NODE:
                                    raise xml.dom.NamespaceErr("illegal use of the 'xmlns' attribute")
                        prefix = None
                        localName = name
            else:
                prefix = None
                localName = None
            if n.nodeType == Node.ATTRIBUTE_NODE:
                element = n.ownerElement
                if element is not None:
                    is_id = n._is_id
                    element.removeAttributeNode(n)
        else:
            element = None
        n.prefix = prefix
        n._localName = localName
        n.namespaceURI = namespaceURI
        n.nodeName = name
        if n.nodeType == Node.ELEMENT_NODE:
            n.tagName = name
        else:
            n.name = name
            if element is not None:
                element.setAttributeNode(n)
                if is_id:
                    element.setIdAttributeNode(n)
            return n


defproperty(Document, 'documentElement', doc='Top-level element of this document.')

def _clone_node(node, deep, newOwnerDocument):
    if node.ownerDocument.isSameNode(newOwnerDocument):
        operation = xml.dom.UserDataHandler.NODE_CLONED
    else:
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
    if node.nodeType == Node.ELEMENT_NODE:
        clone = newOwnerDocument.createElementNS(node.namespaceURI, node.nodeName)
        for attr in node.attributes.values():
            clone.setAttributeNS(attr.namespaceURI, attr.nodeName, attr.value)
            a = clone.getAttributeNodeNS(attr.namespaceURI, attr.localName)
            a.specified = attr.specified

        if deep:
            for child in node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    else:
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            clone = newOwnerDocument.createDocumentFragment()
            if deep:
                for child in node.childNodes:
                    c = _clone_node(child, deep, newOwnerDocument)
                    clone.appendChild(c)

        else:
            if node.nodeType == Node.TEXT_NODE:
                clone = newOwnerDocument.createTextNode(node.data)
            else:
                if node.nodeType == Node.CDATA_SECTION_NODE:
                    clone = newOwnerDocument.createCDATASection(node.data)
                else:
                    if node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
                        clone = newOwnerDocument.createProcessingInstruction(node.target, node.data)
                    else:
                        if node.nodeType == Node.COMMENT_NODE:
                            clone = newOwnerDocument.createComment(node.data)
                        else:
                            if node.nodeType == Node.ATTRIBUTE_NODE:
                                clone = newOwnerDocument.createAttributeNS(node.namespaceURI, node.nodeName)
                                clone.specified = True
                                clone.value = node.value
                            else:
                                if node.nodeType == Node.DOCUMENT_TYPE_NODE:
                                    operation = xml.dom.UserDataHandler.NODE_IMPORTED
                                    clone = newOwnerDocument.implementation.createDocumentType(node.name, node.publicId, node.systemId)
                                    clone.ownerDocument = newOwnerDocument
                                    if deep:
                                        clone.entities._seq = []
                                        clone.notations._seq = []
                                        for n in node.notations._seq:
                                            notation = Notation(n.nodeName, n.publicId, n.systemId)
                                            notation.ownerDocument = newOwnerDocument
                                            clone.notations._seq.append(notation)
                                            if hasattr(n, '_call_user_data_handler'):
                                                n._call_user_data_handler(operation, n, notation)

                                        for e in node.entities._seq:
                                            entity = Entity(e.nodeName, e.publicId, e.systemId, e.notationName)
                                            entity.actualEncoding = e.actualEncoding
                                            entity.encoding = e.encoding
                                            entity.version = e.version
                                            entity.ownerDocument = newOwnerDocument
                                            clone.entities._seq.append(entity)
                                            if hasattr(e, '_call_user_data_handler'):
                                                e._call_user_data_handler(operation, n, entity)

                                else:
                                    raise xml.dom.NotSupportedErr('Cannot clone node %s' % repr(node))
    if hasattr(node, '_call_user_data_handler'):
        node._call_user_data_handler(operation, node, clone)
    return clone


def _nssplit(qualifiedName):
    fields = qualifiedName.split(':', 1)
    if len(fields) == 2:
        return fields
    return (None, fields[0])


def _do_pulldom_parse(func, args, kwargs):
    events = func(*args, **kwargs)
    toktype, rootNode = events.getEvent()
    events.expandNode(rootNode)
    events.clear()
    return rootNode


def parse(file, parser=None, bufsize=None):
    if parser is None:
        if not bufsize:
            from xml.dom import expatbuilder
            return expatbuilder.parse(file)
    from xml.dom import pulldom
    return _do_pulldom_parse(pulldom.parse, (file,), {'parser':parser, 
     'bufsize':bufsize})


def parseString(string, parser=None):
    if parser is None:
        from xml.dom import expatbuilder
        return expatbuilder.parseString(string)
    from xml.dom import pulldom
    return _do_pulldom_parse(pulldom.parseString, (string,), {'parser': parser})


def getDOMImplementation(features=None):
    if features:
        if isinstance(features, str):
            features = domreg._parse_feature_string(features)
        for f, v in features:
            if not Document.implementation.hasFeature(f, v):
                return

    return Document.implementation