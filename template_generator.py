#!/usr/bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Xcode 4 template generator
#
# Based on the original code by Ricardo Quesada. 
# Modifications & Ugly Hacks by Nicolas Goles D. 
#
# LICENSE: MIT
#
# Generates an Xcode4 template given several input parameters.
#
# Format taken from: http://blog.boreal-kiss.net/2011/03/11/a-minimal-project-template-for-xcode-4/
#
# NOTE: Not everything is automated, and some understanding about the Xcode4 template system
# is still needed to use this script properly (read the link above).
# ----------------------------------------------------------------------------
'''
Xcode 4 template generator
'''

__docformat__ = 'restructuredtext'

#Add here whatever you need before your Node
_template_open_body = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>"""

_template_description = None
_template_identifier = None
_template_concrete = "yes"
_template_ancestors = None
_template_kind = "Xcode.Xcode3.ProjectTemplateUnitKind"
_template_close_body = "\n</dict>\n</plist>"
_template_plist_name = "TemplateInfo.plist"
_template_shared_settings = None

# python
import sys
import os
import getopt
import glob
import shutil

class Xcode4Template(object):
	def __init__( self, directory, group=None):
		self.directory = directory
		self.files_to_include = []
		self.wildcard = '*'
		self.ignore_extensions = ['h']
		self.allowed_extensions = ['h', 'c', 'cpp', 'm', 'mm']
		self.ignore_dir_extensions = ['xcodeproj']
		self.group = group					# fixed group name
		self.group_index = 1				# automatic group name taken from path
		self.output = []

	def scandirs(self, path):
		for currentFile in glob.glob( os.path.join(path, self.wildcard) ):
			if os.path.isdir(currentFile):
				name_extension = currentFile.split('.')
				extension = name_extension[-1]
										
				if extension not in self.ignore_dir_extensions:
					self.scandirs(currentFile)
					
			else:
				self.include_file_to_append( currentFile )
   
 	#            
	# append file
	#
	def include_file_to_append ( self, currentFile ):
		currentExtension = currentFile.split('.')
		
		if currentExtension[-1] in self.allowed_extensions:
			self.files_to_include.append( currentFile )

	#
	# append the definitions
	#
	def append_definition( self, output_body, path, group, dont_index ):
		output_body.append("\n\t\t<key>%s</key>" % path )

		output_body.append("\t\t<dict>")
		
		groups = path.split('/')
		
		output_body.append("\t\t\t<key>Group</key>\t\t\t")
		output_body.append("\t\t\t<array>")
		for group in groups[:(len(groups)-1)]:
			output_body.append("\t\t\t\t<string>%s</string>" % group)

		output_body.append("\t\t\t</array>")
		output_body.append("\t\t\t<key>Path</key>\n\t\t\t<string>%s</string>" % path )

		if dont_index:
			output_body.append("\t\t\t<key>TargetIndices</key>\n\t\t\t<array/>")

		output_body.append("\t\t</dict>")

	#
	# Generate the "Definitions" section
	#
	def generate_definitions( self ):	
		output_banner = "\n\n\t<!-- Definitions section -->"
		output_header = "\n\t<key>Definitions</key>"
		output_dict_open = "\n\t<dict>"
		output_dict_close = "\n\t</dict>"

		output_body = []
		for path in self.files_to_include:

			# group name
			group = None
			if self.group is not None:
				group = self.group
			else:
				# obtain group name from directory
				dirs = os.path.dirname(path)
				subdirs = dirs.split('/')
				if self.group_index < len(subdirs):
					group = subdirs[self.group_index]
				else:
					# error
					group = None

			# get the extension
			filename = os.path.basename(path)
			name_extension= filename.split('.')
			extension = None
			if len(name_extension) == 2:
				extension = name_extension[1]
			
			self.append_definition( output_body, path, group, extension in self.ignore_extensions )

		self.output.append( output_banner )
		self.output.append( output_header )
		self.output.append( output_dict_open )
		self.output.append( "\n".join( output_body ) )
		self.output.append( output_dict_close )

	# 
	# Generates the "Nodes" section
	#
	def generate_nodes( self ):
		output_banner = "\n\n\t<!-- Nodes section -->"
		output_header = "\n\t<key>Nodes</key>"
		output_open = "\n\t<array>\n"
		output_close = "\n\t</array>"

		output_body = []
		for path in self.files_to_include:
			output_body.append("\t\t<string>%s</string>" % path )

		self.output.append( output_banner )
		self.output.append( output_header )
		self.output.append( output_open )
		self.output.append( "\n".join( output_body ) )
		self.output.append( output_close )
	  
	#
	#	Format the output plist string
	#
	def format_xml( self ):
		self.output.append( _template_open_body )
		
		if _template_description or _template_identifier or _template_kind:
			self.output.append ("\n\t<!--Header Section-->")
		
		if _template_description != None:
			self.output.append( "\n\t<key>Description</key>\n\t<string>%s</string>" % _template_description )

		if _template_identifier:
			self.output.append( "\n\t<key>Identifier</key>\n\t<string>%s</string>" % _template_identifier )
		
		self.output.append( "\n\t<key>Concrete</key>")
		
		if _template_concrete.lower() == "yes":
			self.output.append( "\n\t<string>True</string>" )
		elif _template_concrete.lower() == "no":
			self.output.append( "\n\t<string>False</string>" )
		
		self.output.append( ("\n\t<key>Kind</key>\n\t<string>%s</string>" % _template_kind) )
		
		if _template_ancestors:
			self.output.append("\n\t<key>Ancestors</key>\n\t<array>")
			ancestors = _template_ancestors.split(" ")
			for ancestor in ancestors:
				self.output.append("\n\t\t<string>%s</string>" % str(ancestor))
			self.output.append("\n\t</array>")
	
		self.generate_definitions()
		self.generate_nodes()
		self.output.append( _template_close_body )
	
	#
	#	Create "TemplateInfo.plist" file.
	#
	def write_xml( self ):
		FILE = open( _template_plist_name, "w" )
		FILE.writelines( self.output )
		FILE.close()

	#
	#	Generates the template directory.
	#
	def generate_directory ( self ):
		if not os.path.exists(self.directory + ".xctemplate"):
		    os.makedirs(self.directory + ".xctemplate")
		
	#
	#	Arrange Files
	#
	def arrange_files ( self ):
		shutil.move( self.directory, self.directory + ".xctemplate" )
		shutil.move( _template_plist_name, self.directory + ".xctemplate")
	
	#
	#	Scan Dirs, format & write.
	#
	def generate( self ):
		self.scandirs( self.directory )
		self.format_xml()
		self.write_xml()

def help():
	print "%s v1.0 - An utility to generate Xcode 4 templates" % sys.argv[0]
	print "Usage:"
	print "\t-c concrete (concrete or \"abstract\" xcode template)"	
	print "\t-d directory (directory to parse)"
	print "\t-g group (group name for Xcode template)"
	print "\t--description \"This template description\""
	print "\t--identifier (string to identify this template)"
	print "\t--ancestors (string separated by spaces containing all ancestor ids)"
	print "\nExample:"
	print "\t%s -d cocos2d --description \"This is my template\" --identifier com.yoursite.template --ancestors com.yoursite.ancestor1 --concrete=False " % sys.argv[0]
	sys.exit(-1)

if __name__ == "__main__":
	if len( sys.argv ) == 1:
		help()

	directory = None
	group = None
	argv = sys.argv[1:]
	try:								
		opts, args = getopt.getopt(argv, "d:g:description:identifier:ancestors:c:s", ["directory=","group=","description=", "identifier=", "ancestors=", "concrete=", "settings="])
		for opt, arg in opts:
			if opt in ("-d","--directory"):
				directory = arg.strip('/')
			elif opt in ("-g","--group"):
				group = arg
			elif opt in ("--description"):
				_template_description = arg
			elif opt in ("--identifier"):
				_template_identifier = arg
			elif opt in ("--ancestors"):
				_template_ancestors = arg
			elif opt in ("-c", "--concrete"):
				_template_concrete = arg
			elif opt in ("-s", "--settings"):
				_template_shared_settings = arg
				
	except getopt.GetoptError,e:
		print e

	if directory == None:
		help()

	gen = Xcode4Template( directory=directory, group=group )
	gen.generate()
	gen.generate_directory()
	gen.arrange_files()
