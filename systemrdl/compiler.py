from copy import deepcopy

from antlr4 import FileStream, CommonTokenStream

from . import messages
from .parser.SystemRDLLexer import SystemRDLLexer
from .parser.SystemRDLParser import SystemRDLParser
from .core.ComponentVisitor import RootVisitor
from .core.properties import PropertyRuleBook
from .core.namespace import NamespaceRegistry
from .core.elaborate import ElabExpressionsListener, PrePlacementValidateListener
from .core.elaborate import StructuralPlacementListener
from .core.validate import ValidateListener
from . import component as comp
from . import walker
from .node import Node

class RDLCompiler:
    
    def __init__(self, message_printer=None):
        """
        RDLCompiler constructor.
        
        Parameters
        ----------
        message_printer: :class:`~systemrdl.messages.MessagePrinter`
            Override the default message printer
        """
        
        # Set up message handling
        if message_printer is None:
            message_printer = messages.MessagePrinter()
        self.msg = messages.MessageHandler(message_printer)
        
        self.namespace = NamespaceRegistry(self)
        self.property_rules = PropertyRuleBook(self)
        
        self.visitor = RootVisitor(self)
        self.root = self.visitor.component
    
    
    def compile_file(self, path):
        """
        Parse & compile a single file and append it to RDLCompiler's root
        namespace
        
        Parameters
        ----------
        path:str
            Path to an RDL source file
        
        Raises
        ------
        :class:`~systemrdl.messages.RDLCompileError`
            If any fatal compile error is encountered
        """
        
        input_stream = FileStream(path)
        
        lexer = SystemRDLLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(messages.RDLAntlrErrorListener(self.msg))
        
        token_stream = CommonTokenStream(lexer)
        
        parser = SystemRDLParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(messages.RDLAntlrErrorListener(self.msg))
        
        # Run Antlr parser on input
        parsed_tree = parser.root()
        if self.msg.error_count:
            self.msg.fatal("Parse aborted due to previous errors")
        
        # Traverse parse tree with RootVisitor
        self.visitor.visit(parsed_tree)
        
        # Reset default property assignments from namespace.
        # They should not leak between files since that would be confusing.
        self.namespace.default_property_ns_stack = [{}]
        
        if self.msg.error_count:
            self.msg.fatal("Compile aborted due to previous errors")
    
    def elaborate(self, top_def_name=None, inst_name=None, parameters=None):
        """
        Elaborates the design with the specified component definition from
        the root namespace as the top-level component.
        
        Currently, an RDLCompiler instance can only be elaborated once.
        
        Parameters
        ----------
        top_def_name: str
            Explicitly choose which addrmap  in the root namespace will be the
            top-level component.
            
            If unset, The last addrmap defined will be chosen.
            
        inst_name: str
            Overrides the top-component's instantiated name.
            By default, instantiated name is the same as ``top_def_name``
        
        parameters: TBD
            Assign the top-component instance parameters
        
        Raises
        ------
        :class:`~systemrdl.messages.RDLCompileError`
            If any fatal elaboration error is encountered
        
        Returns
        -------
        :class:`~systemrdl.node.AddrmapNode`
            Elaborated top-level component's Node object.
        """
        if parameters is None:
            parameters = {}
        
        # Get top-level component definition to elaborate
        if top_def_name is not None:
            # Lookup top_def_name
            if top_def_name not in self.root.comp_defs:
                self.msg.fatal("Elaboration target '%s' not found" % top_def_name)
            top_def = self.root.comp_defs[top_def_name]
            
            if not isinstance(top_def, comp.Addrmap):
                self.msg.fatal("Elaboration target '%s' is not an 'addrmap' component" % top_def_name)
        else:
            # Not specified. Find the last addrmap defined
            for comp_def in reversed(self.root.comp_defs.values()):
                if isinstance(comp_def, comp.Addrmap):
                    top_def = comp_def
                    top_def_name = comp_def.type_name
                    break
            else:
                self.msg.fatal("Could not find any 'addrmap' components to elaborate")
        
        # Create a top-level instance
        top_inst = deepcopy(top_def)
        top_inst.is_instance = True
        if inst_name is not None:
            top_inst.inst_name = inst_name
        else:
            top_inst.inst_name = top_def_name
        
        # Override parameters as needed
        if len(parameters):
            # TODO: Add mechanism to set parameters of top-level component
            raise NotImplementedError
        
        top_node = Node._factory(top_inst, self)
        
        # Resolve all expressions
        walker.RDLWalker(skip_not_present=False).walk(
            top_node,
            ElabExpressionsListener(self.msg)
        )
        
        # Resolve address and field placement
        walker.RDLWalker(skip_not_present=False).walk(
            top_node,
            PrePlacementValidateListener(self.msg),
            StructuralPlacementListener(self.msg)
        )
        
        # Validate design
        walker.RDLWalker().walk(top_node, ValidateListener(self))
        
        if self.msg.error_count:
            self.msg.fatal("Elaborate aborted due to previous errors")
        
        return top_node
