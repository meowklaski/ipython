from IPython.core.display import *
from base64 import *
import os
# coding: utf-8
def fileHTML(filename,info,icon=None):
    innerHTML =""" 
        <table>
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

I=Image(filename='icn.png',embed=True)
st="""
    <style>
        table{ 
            /*background-color :purple;
            border-collapse:collapse;
            border-style:none;
            border-width:0px;
            padding:0px;
            margin:0px;*/
            }
        td.filename {
                        padding:2px; 
                        padding-top:4px;
                        padding-bottom:0px;
                        }
        td.info     {
                    padding:2px;
                    padding-top:0px;
                    font-size : small;
                    }
        td.icon     {
                    margin:5px;
                    padding:2px;
                    }
        img{width:40px;height:40px;}
        .info{color:grey; font-size:medium}
    </style>
"""  

st =  st+'<table><tr>'
lls = get_ipython().getoutput(u'ls')
for i in range(len(lls)):
    if (i)%4 is 0 and i is not 0:
        st = st+'</tr><tr>'
    st = st+'<td>'
    st= st+fileHTML(lls[i],unicode(os.path.getsize(lls[i]))+'bytes',b64encode(I.data))
    st = st+'</td>'
st = st +'</tr></table>'
HTML(st)
