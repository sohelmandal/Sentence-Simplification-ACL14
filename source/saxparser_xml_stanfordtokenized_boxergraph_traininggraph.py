#!/usr/bin/env python
#===================================================================================
#title           : saxparser_xml_stanfordtokenized_boxergraph_traininggraph.py     =
#description     : Boxer-Training-Graph-XML-Handler                                =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================

from xml.sax import handler, make_parser
from boxer_graph_module import Boxer_Graph
from training_graph_module import Training_Graph
from em_inside_outside_algorithm import EM_InsideOutside_Optimiser
import copy

class SAXPARSER_XML_StanfordTokenized_BoxerGraph_TrainingGraph:
    def __init__(self, training_xmlfile, NUM_TRAINING_ITERATION, smt_sentence_pairs, probability_tables, count_tables, METHOD_FEATURE_EXTRACT):
        self.training_xmlfile = training_xmlfile
        self.NUM_TRAINING_ITERATION = NUM_TRAINING_ITERATION
        self.smt_sentence_pairs = smt_sentence_pairs
        self.probability_tables = probability_tables
        self.count_tables = count_tables
        self.METHOD_FEATURE_EXTRACT = METHOD_FEATURE_EXTRACT

        self.em_io_handler = EM_InsideOutside_Optimiser(self.smt_sentence_pairs, self.probability_tables, self.count_tables, self.METHOD_FEATURE_EXTRACT)

    def parse_to_initialize_probabilitytable(self):
        # Initialize probability table and populate self.smt_sentence_pairs
        handler = SAX_Handler("init", self.em_io_handler)
        parser = make_parser()
        parser.setContentHandler(handler)
        print "Start parsing "+self.training_xmlfile+" ..."
        parser.parse(self.training_xmlfile)
        
    def parse_to_iterate_probabilitytable(self):
        handler = SAX_Handler("iter", self.em_io_handler)
        parser = make_parser()
        parser.setContentHandler(handler)
        
        for count in range(self.NUM_TRAINING_ITERATION):
            print "Starting iteration: "+str(count+1)+" ..."

            print "Resetting all counts to ZERO ..."
            self.em_io_handler.reset_count_table()

            print "Start parsing "+self.training_xmlfile+" ..."
            parser.parse(self.training_xmlfile)  
            print "Ending iteration: "+str(count+1)+" ..."
        
            print "Updating probability table ..."
            self.em_io_handler.update_probability_table()
 
class SAX_Handler(handler.ContentHandler):
    def __init__(self, stage, em_io_handler):
        # "init" or "iter" stage
        self.stage = stage
        
        # EM algorithm handler
        self.em_io_handler = em_io_handler
        
        # Sentence Data
        self.sentid = ""
        self.main_sentence = ""
        self.simple_sentencs = []
        self.main_sent_dict = {}
        # Boxer Data
        self.boxer_graph = {"nodes":{}, "relations":{}, "edges":[]}
        # Training Graph Data 
        self.training_graph = {"major-nodes":{}, "oper-nodes":{}, "edges":[]}
        
        # Common TAG variables
        self.isS = False
        self.sentence = ""

        # Main
        self.isMain = False
        self.isWinfo = False
        self.isW = False
        self.word = ""
        self.wid = ""
        self.wpos = ""

        # Simple Set
        self.isSimple = False

        # Boxer
        self.isBoxer = False

        # TrainingGraph
        self.isTrainingGraph = False

        # Node
        self.isNode = False
        self.nodesym = ""

        # Span
        self.isSpan = False

        # pred
        self.isPred = False
        self.predsym = ""

        # relation
        self.isRel = False
        self.relsym = ""
        
        # major oper nodes
        self.isMajorNodes = False
        self.isOperNodes = False

        # type
        self.isType = False
        self.type = ""

        # Nodeset
        self.isNodeset = False

        # Split
        self.isSplitCandidate = False
        self.isSplitCandidateLeft = False
        self.isSC = False
        
        # Out of discourse OOD
        self.isOODCandidates = False
        self.isOODProcessed = False

        # Relations
        self.isRelCandidates = False
        self.isRelProcessed = False
        
        # Modifiers
        self.isModCandidates = False
        self.isModposProcessed = False
        self.isModposFiltered = False

    def startDocument(self):     
        print "Start parsing the document ..."
       
    def endDocument(self):
        print "End parsing the document ..."

    def startElement(self, nameElt, attrOfElt):
        if nameElt == "sentence":
            self.sentid = attrOfElt["id"]
            
            # Refreshing Sentence Data
            self.main_sentence = ""
            self.simple_sentences = []
            self.main_sent_dict = {}
            # Refreshing Boxer Data
            self.boxer_graph = {"nodes":{}, "relations":{}, "edges":[]}
            # Refreshing Training Graph Data 
            self.training_graph = {"major-nodes":{}, "oper-nodes":{}, "edges":[]}
        
        if nameElt == "main":
            self.isMain = True
            
        if nameElt == "s":
            self.isS = True
            self.sentence = ""

        if nameElt == "winfo":
            self.isWinfo = True
            
        if nameElt == "w":
            self.isW = True
            self.word = ""
            self.wid = int(attrOfElt["id"])
            self.wpos = attrOfElt["pos"]
        
        if nameElt == "simple":
            self.isSimple = True
            
        if nameElt == "box":
            self.isBoxer = True

        if nameElt == "train-graph":
            self.isTrainingGraph = True

        if nameElt == "major-nodes":
            self.isMajorNodes = True
            
        if nameElt == "oper-nodes":
            self.isOperNodes = True

        if nameElt == "node":
            self.isNode = True
            self.nodesym = attrOfElt["sym"]
            
            if self.isBoxer == True:
                self.boxer_graph["nodes"][self.nodesym] = {"positions": [], "predicates":[]}
        
            if self.isTrainingGraph == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym] = {"type": "", "nodeset": [], "simple-sentences":[], 
                                                                        "split-candidates":[],
                                                                        "ood-candidates":[], "ood-processed":[],
                                                                        "rel-candidates":[], "rel-processed":[],
                                                                        "mod-candidates":[], "modpos-processed":[], "modpos-filtered":[]}
                    
                if self.isOperNodes == True:
                    self.training_graph["oper-nodes"][self.nodesym] = {"type": "", 
                                                                       "split-candidate":[], "not-split-candidates":[],
                                                                       "ood-candidate":"", "drop-result":"",
                                                                       "rel-candidate":"","mod-candidate":""}

        if nameElt == "rel":
            self.isRel = True
            self.relsym = attrOfElt["sym"]
            
            if self.isBoxer == True:
                self.boxer_graph["relations"][self.relsym] = {"positions": [], "predicates":""}

        if nameElt == "span":
            self.isSpan = True
               
        if nameElt == "pred":
            self.isPred = True
            self.predsym = attrOfElt["sym"]

            if self.isBoxer == True and self.isNode == True:
                self.boxer_graph["nodes"][self.nodesym]["predicates"].append([self.predsym, []])

            if self.isBoxer == True and self.isRel == True:
                self.boxer_graph["relations"][self.relsym]["predicates"] = self.predsym
                
        if nameElt == "loc":
            if self.isBoxer == True and self.isNode == True and self.isSpan == True:
                self.boxer_graph["nodes"][self.nodesym]["positions"].append(int(attrOfElt["id"]))
            
            if self.isBoxer == True and self.isNode == True and self.isPred == True:
                self.boxer_graph["nodes"][self.nodesym]["predicates"][-1][1].append(int(attrOfElt["id"]))

            if self.isBoxer == True and self.isRel == True and self.isSpan == True:
                self.boxer_graph["relations"][self.relsym]["positions"].append(int(attrOfElt["id"]))

            if self.isModposProcessed == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["modpos-processed"].append(int(attrOfElt["id"]))
                    
            if self.isModposFiltered == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["modpos-filtered"].append(int(attrOfElt["id"]))
                    
        if nameElt == "edge":
            if self.isBoxer == True:
                self.boxer_graph["edges"].append((attrOfElt["par"], attrOfElt["dep"], attrOfElt["lab"]))

            if self.isTrainingGraph == True:
                self.training_graph["edges"].append((attrOfElt["par"], attrOfElt["dep"], attrOfElt["lab"]))
                
        if nameElt == "type":
            self.isType = True
            self.type = ""
            
        if nameElt == "nodeset":
            self.isNodeset = True

        if nameElt == "n":
            if self.isNodeset == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["nodeset"].append(attrOfElt["sym"])
            if self.isSC == True:
                if self.isSplitCandidate == True:
                    if self.isMajorNodes == True:
                        self.training_graph["major-nodes"][self.nodesym]["split-candidates"][-1].append(attrOfElt["sym"])
                    if self.isOperNodes == True:
                        self.training_graph["oper-nodes"][self.nodesym]["split-candidate"].append(attrOfElt["sym"])
                if self.isSplitCandidateLeft == True:
                    if self.isOperNodes == True:
                        self.training_graph["oper-nodes"][self.nodesym]["not-split-candidates"][-1].append(attrOfElt["sym"])
            
            if self.isOODCandidates == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["ood-candidates"].append(attrOfElt["sym"])
                if self.isOperNodes == True:
                    self.training_graph["oper-nodes"][self.nodesym]["ood-candidate"] = attrOfElt["sym"]
                    
            if self.isOODProcessed == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["ood-processed"].append(attrOfElt["sym"])

            if self.isRelCandidates == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["rel-candidates"].append(attrOfElt["sym"])
                if self.isOperNodes == True:
                    self.training_graph["oper-nodes"][self.nodesym]["rel-candidate"] = attrOfElt["sym"]
                
            if self.isRelProcessed == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["rel-processed"].append(attrOfElt["sym"])

            if self.isModCandidates == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["mod-candidates"].append((attrOfElt["loc"], attrOfElt["sym"]))
                if self.isOperNodes == True:
                    self.training_graph["oper-nodes"][self.nodesym]["mod-candidate"] = (attrOfElt["loc"], attrOfElt["sym"])
                    
        if nameElt == "split-candidates" or nameElt == "split-candidate-applied":
            self.isSplitCandidate = True
            
        if nameElt == "split-candidate-left":
            self.isSplitCandidateLeft = True
            
        if nameElt == "sc":
            self.isSC = True
            if self.isSplitCandidate == True:
                if self.isMajorNodes == True:
                    self.training_graph["major-nodes"][self.nodesym]["split-candidates"].append([])
                if self.isOperNodes == True:
                    self.training_graph["oper-nodes"][self.nodesym]["split-candidate"] = []
            if self.isSplitCandidateLeft == True:
                if self.isOperNodes == True:
                    self.training_graph["oper-nodes"][self.nodesym]["not-split-candidates"].append([])
    
        if nameElt == "ood-candidate" or nameElt == "ood-candidates":
            self.isOODCandidates = True

        if nameElt == "ood-processed":
            self.isOODProcessed = True

        if nameElt == "rel-candidate" or nameElt == "rel-candidates":
            self.isRelCandidates = True

        if nameElt == "rel-processed":
            self.isRelProcessed = True

        if nameElt == "mod-candidate" or nameElt == "mod-candidates":
            self.isModCandidates = True

        if nameElt == "mod-loc-processed":
            self.isModposProcessed = True
        
        if nameElt == "mod-loc-filtered":
            self.isModposFiltered = True

        if nameElt == "is-dropped":
            if self.isOperNodes == True:
                self.training_graph["oper-nodes"][self.nodesym]["drop-result"] = attrOfElt["val"]

    def endElement(self, nameElt):
        if nameElt == "sentence":
            # print self.sentid
            # print
            # print self.main_sentence
            # print 
            # print self.main_sent_dict
            # print
            # print self.simple_sentences
            # print
            # print self.boxer_graph
            # print
            # print self.training_graph

            # Creating the original format of Boxer and Training Graph
            final_boxer_graph = Boxer_Graph()
            for nodename in self.boxer_graph["nodes"]:
                final_boxer_graph.nodes[nodename] = copy.copy(self.boxer_graph["nodes"][nodename])
            for nodename in self.boxer_graph["relations"]:
                final_boxer_graph.relations[nodename] = copy.copy(self.boxer_graph["relations"][nodename])
            final_boxer_graph.edges = self.boxer_graph["edges"][:]
            
            final_training_graph = Training_Graph()
            for nodename in self.training_graph["major-nodes"]:
                nodedict = self.training_graph["major-nodes"][nodename]
                if nodedict["type"] == "split":
                    final_training_graph.major_nodes[nodename] = (nodedict["type"], nodedict["nodeset"][:], nodedict["simple-sentences"][:], nodedict["split-candidates"][:])
                if nodedict["type"] == "drop-rel":
                    final_training_graph.major_nodes[nodename] = (nodedict["type"], nodedict["nodeset"][:], nodedict["simple-sentences"][:], nodedict["rel-candidates"][:], 
                                                                  nodedict["rel-processed"][:], nodedict["modpos-filtered"][:])
                if nodedict["type"] == "drop-mod":
                    final_training_graph.major_nodes[nodename] = (nodedict["type"], nodedict["nodeset"][:], nodedict["simple-sentences"][:], nodedict["mod-candidates"][:], 
                                                                  nodedict["modpos-processed"][:], nodedict["modpos-filtered"][:])
                if nodedict["type"] == "drop-ood":
                    final_training_graph.major_nodes[nodename] = (nodedict["type"], nodedict["nodeset"][:], nodedict["simple-sentences"][:], nodedict["ood-candidates"][:], 
                                                                  nodedict["ood-processed"][:], nodedict["modpos-filtered"][:])
                if nodedict["type"] == "fin":
                    final_training_graph.major_nodes[nodename] = (nodedict["type"], nodedict["nodeset"][:], nodedict["simple-sentences"][:], nodedict["modpos-filtered"][:])
            for nodename in self.training_graph["oper-nodes"]:
                nodedict = self.training_graph["oper-nodes"][nodename]
                if nodedict["type"] == "split":
                    if len(nodedict["split-candidate"]) == 0:
                        final_training_graph.oper_nodes[nodename] = (nodedict["type"], None, nodedict["not-split-candidates"][:])
                    else:
                        final_training_graph.oper_nodes[nodename] = (nodedict["type"], nodedict["split-candidate"], nodedict["not-split-candidates"][:])
                if nodedict["type"] == "drop-rel":
                    final_training_graph.oper_nodes[nodename] = (nodedict["type"], nodedict["rel-candidate"], nodedict["drop-result"])
                if nodedict["type"] == "drop-mod":
                    final_training_graph.oper_nodes[nodename] = (nodedict["type"], nodedict["mod-candidate"], nodedict["drop-result"])
                if nodedict["type"] == "drop-ood":
                    final_training_graph.oper_nodes[nodename] = (nodedict["type"], nodedict["ood-candidate"], nodedict["drop-result"])
            final_training_graph.edges = self.training_graph["edges"][:]

            # Process various stage "init" or "iter"
            if self.stage == "init":
                self.em_io_handler.initialize_probabilitytable_smt_input(self.sentid, self.main_sentence, self.main_sent_dict, self.simple_sentences, final_boxer_graph, final_training_graph)
            
            if self.stage == "iter":
                self.em_io_handler.iterate_over_probabilitytable(self.sentid, self.main_sentence, self.main_sent_dict, self.simple_sentences, final_boxer_graph, final_training_graph)

            if int(self.sentid)%10000 == 0:
                print self.sentid + " training data processed ..."            

        if nameElt == "main":
            self.isMain = False
            
        if nameElt == "s":
            self.isS = False
            
            if self.isMain == True:
                self.main_sentence = self.sentence

            if self.isSimple == True:
                if self.isNode == True:
                    if self.isMajorNodes == True:
                        self.training_graph["major-nodes"][self.nodesym]["simple-sentences"].append(self.sentence)
                else:
                    self.simple_sentences.append(self.sentence)

        if nameElt == "winfo":
            self.isWinfo = False
            
        if nameElt == "w":
            self.isW = False
            
            if self.isWinfo == True:
                self.main_sent_dict[self.wid] = (self.word, self.wpos) 

        if nameElt == "simple":
            self.isSimple = False

        if nameElt == "box":
            self.isBoxer = False

        if nameElt == "train-graph":
            self.isTrainingGraph = False        

        if nameElt == "major-nodes":
            self.isMajorNodes = False
            
        if nameElt == "oper-nodes":
            self.isOperNodes = False          

        if nameElt == "node":
            self.isNode = False

        if nameElt == "rel":
            self.isRel = False

        if nameElt == "span":
            self.isSpan = False

        if nameElt == "pred":
            self.isPred = False

        if nameElt == "type":
            self.isType = False
            if self.isMajorNodes == True:
                self.training_graph["major-nodes"][self.nodesym]["type"] = self.type
            if self.isOperNodes == True:
                self.training_graph["oper-nodes"][self.nodesym]["type"] = self.type

        if nameElt == "nodeset":
            self.isNodeset = False

        if nameElt == "split-candidates" or nameElt == "split-candidate-applied":
            self.isSplitCandidate = False
            
        if nameElt == "split-candidate-left":
            self.isSplitCandidateLeft = False
            
        if nameElt == "sc":
            self.isSC = False
    
        if nameElt == "ood-candidate" or nameElt == "ood-candidates":
            self.isOODCandidates = False

        if nameElt == "ood-processed":
            self.isOODProcessed = False

        if nameElt == "rel-candidate" or nameElt == "rel-candidates":
            self.isRelCandidates = False

        if nameElt == "rel-processed":
            self.isRelProcessed = False

        if nameElt == "mod-candidate" or nameElt == "mod-candidates":
            self.isModCandidates = False

        if nameElt == "mod-loc-processed":
            self.isModposProcessed = False
        
        if nameElt == "mod-loc-filtered":
            self.isModposFiltered = False

    def characters(self, chrs):
        if self.isS:
            self.sentence += chrs

        if self.isW:
            self.word += chrs

        if self.isType:
            self.type += chrs
