from IPython.core.display import *
from base64 import *
import os
from math import ceil
# coding: utf-8

def NoneTranspose(listlike,step=4):
    l = len(listlike)
    rows = int(ceil(l/step))+1
    ind = lambda i,j : i*rows+j
    transposed = zip(*[[ ind(i,j) if ind(i,j) < l else None for j in range(rows)] for i in range(step)])
    return [item for sublist in transposed for item in sublist]

def fileHTML(filename,info,icon=None):
    innerHTML =""" 
        <table class='noborder'>
        <tr>
            <td rowspan=2 class='icon'>
            <img src="data:image/png;base64,\n%s\n"/></td>
            <td class='filename'>%s</td>
        </tr>
        <tr>
            <td class='info'>%s</td>
        </tr>
        </table>"""
    return innerHTML % (icon,filename,info)

def pls(columns=6):
    I=Image(filename='icn.png',embed=True)
    st="""
        <style>
            .rendered_html *,*{margin:0px; padding:0px}
            table{ 
                /*background-color :purple;
                border-color:green;
                border-width:1px;*/
                }
            tr,td,table {padding:0px; margin:0px;}
            table *, table.noborder,table.noborder *
            {
                background-color : none;
                border-width:0px;
                border :none;
                birder-collapsed:collapsed;
                padding:0px;
                margin:0px;
            }
            /*td{background-color:red}
            img{
                background-color :green;
                border-color:green;
                border-width:2px;
            }*/
            td.filename {
                            line-height:15px;
                            padding:2px; 
                            padding-top:5px;
                            padding-bottom:0px;
                            }
            td.info     {
                            line-height:15px;
                        padding:2px;
                        padding-top:0px;
                        font-size : small;
                        }
            td.icon     {
                        margin:5px;
                        padding:2px;
                        }
            /*img{width:40px;height:40px;}*/
            .info{color:grey; font-size:medium}
        </style>
    """  

    st =  st+'<table class="noborder"><tr>'
    lls = get_ipython().getoutput(u'ls')
    index = NoneTranspose(range(len(lls)),step=columns)
    for i in xrange(len(index)):
        if (i)%columns is 0 and i is not 0:
            st = st+'</tr><tr>'
        ind = index[i]
        st = st+'<td>'
        # warning, 0 is not None, so no if ind by itself
        if ind is not None:
            # st= st+str(ind)
            try :
                st= st+fileHTML(lls[ind],unicode(os.path.getsize(lls[ind]))+'bytes',b64encode(I.data))
            except :
                print(ind,'/',len(lls))

        st = st+'</td>'
    st = st +'</tr></table>'
    return HTML(st)
