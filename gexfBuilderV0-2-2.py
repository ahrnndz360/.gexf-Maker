##VERSION: 0.2.2
##change log:
## 1. now accept intervals as a timerepresentation
## 2. ids, timestamps, and intervals needn't be passed as strings anymore

import xml.etree.ElementTree as ET
import xml.dom.minidom
import sys

##global variable used for checking for valid function perarameters
##this may not be needed
keywords = ({
		'graphTR':['timestamp','interval'],
		'graphE':['directed','undirected'],
		'graphTF':['double','date'],
		'attributesT':['integer', 'double', 'boolean', 'string', 'list-string']
})

class gexfTree(object):

	##Build a skeleton gexf frame element based on desired mode
	##Required: mode, edgtype,  time format(If mode == dynamic) and time representation(If mode == dynamic)
	def __init__(self, mode, edgetype, timeF=None, timeR=None):
		##dictionaries to quickly check if an id has already been used for a class 
		self.attributeDict ={}
		self.nodeDict = {}
		self.edgeDict = {}
		##used to accept intervals lists or timeStamps lists
		self.timeRep = timeR
		
		self.gexf = ET.Element('gexf', {'version':'1.3'})
		                                                             
		##create a dynamic gexfTree
		if mode == 'dynamic':
			if timeR in keywords['graphTR'] and timeF in keywords['graphTF']:
				self.graph = ET.Element('graph', {'mode':mode, 'defaultedgetype':edgetype, 'timeformat':timeF, 'timerepresentation':timeR})
				##create subelements for housing dynamic attributes
				ET.SubElement(self.graph, 'attributes', {'class':'node', 'mode':'dynamic'})
				ET.SubElement(self.graph, 'attributes', {'class':'edge', 'mode':'dynamic'})
				
			else:
				raise ValueError(timeF, timeR)
		##create a static a graph	
		elif mode == 'static':
			if edgetype in keywords['graphE']:   
				self.graph = ET.Element('graph', {'mode':mode, 'defaultedgetype':edgetype})
			else:                                 
				raise ValueError(edgetype) 
		else:
			raise ValueError(mode)
		
		##create subelements for housing edges, node and static attributes
		ET.SubElement(self.graph, 'attributes', {'class':'node', 'mode':'static'})
		ET.SubElement(self.graph, 'attributes', {'class':'edge', 'mode':'static'})
		ET.SubElement(self.graph, 'nodes')
		ET.SubElement(self.graph, 'edges')
		
		self.gexf.append(self.graph)                                                          
		
	
	
	##Add attribute to existing gexf element
	##Required: attribute class, id, title, type for value
	##Optional: mode(defaults to static), default value
	##Caveat: default values may be deprecated in gexf v1.3
	def addAttribute(self, clss, id, title, type, mode=None, default=None):
		id = str(id)
		if not type in keywords['attributesT']:
			raise ValueError(type)
		if not id in self.attributeDict:
			##find proper parent element for attribute
			if mode:                                                                                                          
				attributes = self.graph.find('.//attributes[@class="%s"][@mode="%s"]'%(clss,mode))
			else:
				attributes = self.graph.find('.//attributes[@class="%s"][@mode="static"]'%(clss))
			
			##create attribute element and attach to attributes
			ET.SubElement(attributes, 'attribute', {'id':id, 'title':str(title), 'type':type})
			self.attributeDict[id] = [clss, title, type, mode, default] 
		else:
			raise ValueError(id + 'already exists')
	
	##Add node to gexf object
	##Required: id
	##Optional: label(defaults to same value as id), list of timestamps, list of intervals(not currently supported)
	def addNodes(self, id, label=None, timeStamps=None, intervals=None):
		
		##check if node id already exists in graph
		id = str(id)
		if not id in self.nodeDict:
			##create node element and subelements for node
			nodes= self.graph.find('nodes')
			if label:
				node = ET.Element('node', {'id':id, 'label':label})
			else:
				node = ET.Element('node', {'id':id})
				ET.SubElement(node, 'attvalues')
			spells = ET.Element('spells')
			
			##add a spell under spells element for every timestamp or interval provided
			if timeStamps and self.timeRep == 'timestamp':
				for ts in timeStamps:
					ET.SubElement(spells, 'spell', {'timestamp':str(ts)})
					
			if intervals and self.timeRep == 'interval':
				for inter in invervals:
					ET.SubElement(spells, 'spell', {'interval':str(interval)})
			
			node.append(spells)
			nodes.append(node)
			
			##changing dict to include etree element
			self.nodeDict[id] = node
		
		else:
			raise ValueError('node: '+str(id)+' already exists')
			
	##Add Edges to gexf object
	##Required: id, source node, target node
	##Optional: label(defaults to id), list of time stamps, list intervals(not supported)
	##ToDo: accept list of edges | 
	def addEdges(self, id, source, target, label=None, kind =None, timeStamps=None, intervals=None):
		##check if edge id already exists in graph
		id = str(id)
		source = str(source)
		target = str(target)
		if not source in self.nodeDict or not target in self.nodeDict:
			raise ValueError( 'Node ' + source + " or " + target+ " does not exist")
		
		if not id in self.edgeDict:
			##create edge element and subelements for edges 
			edges = self.graph.find('edges')
			if label:
				if kind:
					edge = ET.Element('edge', {'id':id, 'label':label, 'kind':kind, 'source':source, 'target':target})
				else:
					edge = ET.Element('edge', {'id':id, 'label':label, 'source':source, 'target':target})
			else:
				if kind:
					edge = ET.Element('edge', {'id':id,'kind':kind, 'source':source, 'target':target})
				else:
					edge = ET.Element('edge', {'id':id, 'source':source, 'target':target})
			ET.SubElement(edge, 'attvalues')
			spells = ET.Element('spells')                                                                                               
			                                                                                                    
			##add a spell under spells for every timestamp provided
			if timeStamps and self.timeRep == 'timestamp':
				for ts in timeStamps:
					ET.SubElement(spells, 'spell', {'timestamp':str(ts)})
					
			if intervals and self.timeRep == 'interval':
				for inter in inverals:
					ET.SubElement(spells, 'spell', {'interval':str(interval)})
					
			edge.append(spells)
			edges.append(edge)
			self.edgeDict[id] = edge
		
		else:
			raise ValueError('edge: '+str(id)+' already exists')
		
	##Add attvalue to  nodes or edges
	##Required: class for attribute, 
	##Work with just timestamps for now, modify to add other timereps later
	##Caveat: copies one existing dictionary for the sake avoiding redundancy in the code
	##ToDo: implement check if target attribute requires timestamp or not                                                                   
	def addAttvalues(self, clss, clssIds, attId, value, timeStamps=None, intervals=None):
		##check if attribute exists
		attId = str(attId)
		if not attId in self.attributeDict:	
			raise ValueError(attId + ' is not an available attribute')
		
		##find proper dict to reference from 
		if clss == 'node':
			dict= self.nodeDict
		elif clss =="edge":
			dict = self.edgeDict
		else:
			raise ValueError(clss)	
		
		## insert attvalue element under attvalues element for every node/edge provided
		for clssId in clssIds:
			##check if edge/node exists in gexftree
			clssId = str(clssId)
			if not clssId in dict:
				raise ValueError(str(clssId)+' is not an available '+clss)
			else:
				child = dict[clssId]
				attvalues = child.find('attvalues')
				
				##add same attvalue for every timestamp provided if timestamps are provided
				if timeStamps and self.timeRep == 'timestamp':
					for ts in timeStamps:
						ET.SubElement(attvalues, 'attvalue', {'for':attId,'value':str(value),'timestamp':str(ts)})
				if intervals and self.timeRep == 'interval':
					for inter in timeStamps:
						ET.SubElement(attvalues, 'attvalue', {'for':attId,'value':str(value),'timestamp':str(inter)})
						
				else:
					ET.SubElement(attvalues, 'attvalue', {'for':attId,'value':str(value)})
	
	##Add a list of spells to an edge or node or list of either
	
	##Caveat: copies one existing dictionary for the sake avoiding redundancy in the code
	##ToDO: determine if a check should be implemented to see if timestamp already exists
	def addSpells(self, clss, clssIds, times=None):
		##determine class of spells
		if clss == 'node':
			dict= self.nodeDict
			pElement = self.graph.find('nodes')
		elif clss =="edge":
			dict = self.edgeDict
			pElement = self.graph.find('edges')
		else:
			raise ValueError(clss)
		
		##add a spell element to spells element for every timestamp for every node/edge provided
		for clssId in clssIds:
				##check if edge/node exists in gexftree
				clssId = str(clssId)
				if not clssId in dict:
					raise ValueError(clssId+' is not an available '+clss)
				else:
					child = dict[clssId] 
					spells = child.find('spells')
					for ts in times:
						ET.SubElement(spells, 'spell', {self.timeRep:str(ts)})
					
	##Write	out to file	
	##Required: name of file to write to
	##Caveats: xml file is not pretty printed | extension should always be .gexf	
	def write(self, outfile):
		Tree = ET.ElementTree(self.gexf)
		Tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

##Utility function to print out to console a legible version of the xml file
##Required: file to read xml out from
##ToDo: Find a way to pretty print to console or pretty print to xml if needed from gexfTree object 
##caveat: the function reads from already existing xml file, not from gexftreee object
def pretty(targetfile):
		output = xml.dom.minidom.parse(targetfile)
		pretty_output = output.toprettyxml()
		print pretty_output
		
#test main					
def main():
	g1 = gexfTree('dynamic', 'undirected', 'double', 'timestamp')
	g1.addAttribute('node',0, 'haspenalties', 'boolean')
	g1.addNodes(0, timeStamps=[1])
	g1.addNodes(1)
	g1.addNodes(3)
	g1.addNodes(2)
	g1.addSpells('node', [0,1], [1,2,3])
	g1.addAttvalues('node',[1], 0, 'true')
	g1.addEdges(0, 0, 1 ,kind='EdgeT2')
	g1.addEdges(2, 0, 1 ,kind='EdgeT1' )
	g1.addEdges(1, 1, 2)
	g1.addSpells('edge', [0,2], [1,2,3])
	g1.addSpells('edge', [2], [1,2,3])
	g1.addSpells('edge', [1], [1])
	g1.write('test_gexfBuilder_0-2-0.gexf')
	pretty('test_gexfBuilder_0-2-0.gexf')
	##ET.dump(g1.gexf)
	return
	
	
if __name__ == '__main__':
	main()                                                                                     