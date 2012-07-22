# -*- coding: utf-8 -*-
"""
Extension to provide local encryption of particular cell of the notebook.

Useful to embed solution of exercises into a notebook, and release the solution later, 
by only giving password.
"""
#-----------------------------------------------------------------------------
# Copyright (C) 2010-2011, IPython Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import io
import os, sys
import imp

from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.display import HTML, Javascript, display_javascript, display_html

jscript = r"""
IPython = (function(IPython){

    var PyCrypt = function(){}
    var script_root = '/static/js/pidcrypt/';
    var decrypt_hash = '##--jsext-decrypt--';
    var encrypt_hash = '##--jsext-crypt--';     
    
    var scpts =["pidcrypt.js",
                "pidcrypt_util.js",
                "md5.js",
                "aes_core.js",
                "aes_cbc.js" ];
    
    for(var i=0 ; i< scpts.length ; i++){
        var script = document.createElement( 'script' );
        script.type = 'text/javascript';
        script.src = script_root+scpts[i];
        $("head").append( script );
    }
    
    var allbutfirst = function(textblock){
        var lines = textblock.split('\n');
        lines.splice(0,1);
        return lines.join('\n');   
    }
    
    PyCrypt.prototype.encrypt_cell = function(cn,p){
        var aes = new pidCrypt.AES.CBC();
        var options = {nBits:256};
        var txt = allbutfirst(IPython.notebook.get_cell(cn).get_text())
        if(IPython.notebook.get_cell(cn).code_mirror.getLine(0) === encrypt_hash){
            aes.initEncrypt(txt, p, options);
            var enc = aes.encrypt()
            IPython.notebook.get_cell(cn).set_text(decrypt_hash+'\n'+enc)
        } else {
            console.log('no header, not encrypting');
        }
    }
  
    PyCrypt.prototype.decrypt_cell = function(cn,p){
        var aes = new pidCrypt.AES.CBC();
        var options = {nBits:256};
        var txt = allbutfirst(IPython.notebook.get_cell(cn).get_text())
        if(IPython.notebook.get_cell(cn).code_mirror.getLine(0) === decrypt_hash){
            aes.initDecrypt(txt, p, options);
            var dec = aes.decrypt();
            if( dec != ''){
                IPython.notebook.get_cell(cn).set_text(encrypt_hash+'\n'+dec)
            } else {
                console.log('unable to decryt cell ',i);
            }
        }                
    }
        
    PyCrypt.prototype.encrypt_all_cells = function(p){
        for(var i in IPython.notebook.get_cells())
            {this.encrypt_cell(i,p)}
    }
        
    PyCrypt.prototype.decrypt_all_cells = function(p){
        for(var i in IPython.notebook.get_cells())
            {this.decrypt_cell(i,p)}
    }

    IPython.PyCrypt = PyCrypt;
    return IPython;

})(IPython)

IPython.pycrypt = new IPython.PyCrypt();
"""

doencrypt = """
var p=prompt("Encrypt with password :");
IPython.pycrypt.encrypt_all_cells(p);
console.log('done enc')
"""

dodecrypt = """
var p=prompt("Decrypt with password :");
IPython.pycrypt.decrypt_all_cells(p);
"""


html = r""" 
Put the header <pre>##--jsext-crypt--</pre> on the first line of cells you want to
crypt.<br/>

Click on <a href='' OnClick='var p=prompt("Encrypt with password :");IPython.pycrypt.encrypt_all_cells(p);return false;'> Encrypt </a>, you will be promped for a
password.<br/>

To decript, click on  <a href='' OnClick='var p=prompt("Decrypt with password :");IPython.pycrypt.decrypt_all_cells(p);return false;'>Decrypt</a>, and enter the password to
decode.
"""

@magics_class
class CryptCellsMagics(Magics):

    @line_magic
    def crypt_links(self, line, cell=None):
        """Show a link to crypt/decrypt cells in notebook.
        """
        display_html(HTML(html))
        display_javascript(Javascript(data=jscript))

    @line_magic
    def crypt_logic_only(self, line, cell=None):
        """only send js to frontend, write your own code in mdcell
        """
        display_html(HTML(html))

    @line_magic
    def encrypt_cells(self, line, cell=None):
        display_javascript(Javascript(jscript+doencrypt))

    @line_magic
    def decrypt_cells(self, line, cell=None):
        display_javascript(Javascript(jscript+dodecrypt))
        
_loaded = False

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(CryptCellsMagics)
        _loaded = True
