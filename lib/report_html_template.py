
import re
import html


def preptext_html_alreadyescaped(s):
    if re.match(r'[<>]',re.sub(r'(?:<<(?:ADDED|ENDADDED|REMOVED|ENDREMOVED)>>|&#60;&#60;HIDDENLINEBREAK&#62;&#62;)','',s)):
        raise Exception('Create HTML report: Field values should already be escaped in the input source. Some field contains "<" or ">". Please revise: {field}'.format(field=s))
    return re.sub(r'<<ADDED>>','<span class="mdmdiff-inlineoverlay-added">',re.sub(r'<<REMOVED>>','<span class="mdmdiff-inlineoverlay-removed">',re.sub(r'<<(?:ENDADDED|ENDREMOVED)>>','</span>',re.sub(r'&#60;&#60;HIDDENLINEBREAK&#62;&#62;','<!-- HIDDENLINEBREAK --><br />',s))))

def preptext_html_needsescaping(s):
    s = re.sub(r'(?:&#60;|<)(?:&#60;|<)HIDDENLINEBREAK(?:&#62;|>)(?:&#62;|>)','<!-- HIDDENLINEBREAK --><br />',s)
    s = html.escape(s)
    return s.replace(html.escape('<<ADDED>>'),'<span class="mdmdiff-inlineoverlay-added">').replace(html.escape('<<REMOVED>>'),'<span class="mdmdiff-inlineoverlay-removed">').replace(html.escape('<<ENDADDED>>'),'replacement').replace(html.escape('<<ENDREMOVED>>'),'</span>').replace(html.escape('<!-- HIDDENLINEBREAK --><br />'),'<!-- HIDDENLINEBREAK --><br />')




TEMPLATE_HTML_CSS_NORMALIZECSS = """
article,aside,details,figcaption,figure,footer,header,hgroup,nav,section,summary{display:block;}audio,canvas,video{display:inline-block;*display:inline;*zoom:1;}audio:not([controls]) {display:none;height:0;}[hidden]{display:none;}html{font-size:100%;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}html,button,input,select,textarea{font-family:sans-serif;}body{margin:0;}a:focus{outline:thin dotted;}a:active,a:hover{outline:0;}h1{font-size:2em;margin:0.67em 0;}h2{font-size:1.5em;margin:0.83em 0;}h3{font-size:1.17em;margin:1em 0;}h4{font-size:1em;margin:1.33em 0;}h5{font-size:0.83em;margin:1.67em 0;}h6{font-size:0.75em;margin:2.33em 0;}abbr[title]{border-bottom:1px dotted;}b,strong{font-weight:bold;}blockquote{margin:1em 40px;}dfn{font-style:italic;}mark{background:#ff0;color:#000;}p,pre{margin:1em 0;}code,kbd,pre,samp{font-family:monospace,serif;_font-family:'courier new',monospace;font-size:1em;}pre{white-space:pre;white-space:pre-wrap;word-wrap:break-word;}q{quotes:none;}q:before,q:after{content:'';content:none;}small{font-size:75%;}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline;}sup{top:-0.5em;}sub{bottom:-0.25em;}dl,menu,ol,ul{margin:1em 0;}dd{margin:0 0 0 40px;}menu,ol,ul{padding:0 0 0 40px;}nav ul,nav ol{list-style:none;list-style-image:none;}img{border:0;-ms-interpolation-mode:bicubic;}svg:not(:root) {overflow:hidden;}figure{margin:0;}form{margin:0;}fieldset{border:1px solid #c0c0c0;margin:0 2px;padding:0.35em 0.625em 0.75em;}legend{border:0;padding:0;white-space:normal;*margin-left:-7px;}button,input,select,textarea{font-size:100%;margin:0;vertical-align:baseline;*vertical-align:middle;}button,input{line-height:normal;}button,html input[type="button"],input[type="reset"],input[type="submit"]{-webkit-appearance:button;cursor:pointer;*overflow:visible;}button[disabled],input[disabled]{cursor:default;}input[type="checkbox"],input[type="radio"]{box-sizing:border-box;padding:0;*height:13px;*width:13px;}input[type="search"]{-webkit-appearance:textfield;-moz-box-sizing:content-box;-webkit-box-sizing:content-box;box-sizing:content-box;}input[type="search"]::-webkit-search-cancel-button,input[type="search"]::-webkit-search-decoration{-webkit-appearance:none;}button::-moz-focus-inner,input::-moz-focus-inner{border:0;padding:0;}textarea{overflow:auto;vertical-align:top;}table{border-collapse:collapse;border-spacing:0;}
    """

TEMPLATE_HTML_STYLES = """
    body {
        font-size: 14px;
        Font-family: "Helvetica";
    }
    .clearfix:after {
       content: " "; /* Older browser do not support empty content */
       visibility: hidden;
       display: block;
       height: 0;
       clear: both;
    }
   .error {
        color: #cc0000;
        font-weight: 500;
    }
   .container {
        margin: 0 15px 0;
    }
    @media all and (min-width: 1300px) {
        .container {
            margin: 0 auto 0;
            width: 1200px;
        }
    }
    @media all and (min-width: 1650px) {
        .container {
            margin: 0 auto 0;
            width: 1500px;
        }
    }
    @media all and (min-width: 1800px) {
        .container {
            margin: 0 auto 0;
            width: 1700px;
        }
    }
    h1 {
        font-weight: 700;
        font-size: 32px;
        color: #333;
        margin: 0;
        padding: 0px 0 30px;
    }
    h2 {
        font-weight: 700;
        font-size: 21px;
        color: #222;
        margin: 0;
        padding: 22.5px 0 7.5px;
    }
    h3 {
        font-weight: 700;
        font-size: 17px;
        color: #111;
        margin: 0;
        padding: 22.5px 0 7.5px;
    }
    .header {
        padding: 15px 0 15px;
        border-bottom: 1px solid #eee;
    }
    .footer {
        padding: 15px 0 15px;
        border-top: 1px solid #eee;
    }
    .main {
        padding: 15px 0 15px;
    }
    .wrapper {
        width: 100%; max-width: 100%; overflow-x: auto;
    }
    .mdmreport-banner {
        display: block; position: relative; padding: 1em; margin: 0 0 1em; border: #ddd solid 1px;
    }
"""

TEMPLATE_HTML_STYLES_TABLE = """
.mdmreport-table-wrapper {
    /* font-size: 12px; */
    font-size: 13px;
}
.mdmreport-table, mdmreport-table tbody, .mdmreport-table thead, .mdmreport-table tr, .mdmreport-table td {
    margin: 0;
    padding: 0;
    line-height: 16px;
    border-collapse: collapse; border-spacing: 1px;
    border: 1px #ddd solid;
}

.mdmreport-table { width: 100%; min-width: 100%; max-width: 100%; }

.mdmreport-table tr td {
    vertical-align: top;
}

.mdmreport-contentcell, .mdmreport-contentcell pre {
    font-family: monospace, monospace;
    font-size: 100%;
}
.mdmreport-contentcell pre {
    white-space: pre;
    overflow-x: scroll;
}
.mdmreport-contentcell p {
    margin: 0;
}

.mdmreportpage-type-MDDDiff .mdmreport-table td.mdmreport-colindex-0 {
    padding: 0.25em;
    /* font-size: 89%; */
    width: 5em; min-width: 5em; max-width: 5em;
    overflow-x: hidden;
    white-space: nowrap;
}

.mdmreport-table .mdmreport-record {
    background: #fff;
    transition: all 200ms ease;
}

.mdmreport-table .mdmreport-record:hover {
    background: #efefef;
}

/* all regular cells */ .mdmreport-table .mdmreport-record td {
    padding: 0.25em 0.5em;
    max-width: 15em;
    overflow: hidden;
    overflow-wrap: anywhere;
}
/* first cell with item name */ .mdmreport-table .mdmreport-record td:first-child {
    max-width: 45em;
    overflow: visible;
}
/* 2nd cell with label */ .mdmreport-table .mdmreport-record td:first-child + td {
    max-width: 45em;
}
/* first row */ .mdmreport-table .mdmreport-record:first-child td {
    font-weight: 600;
    padding-top: 0.85em;
    padding-bottom: 0.85em;
}




.mdmreport-table .mdmreport-record {
    position: relative;
}
.mdmreport-table .mdmreport-record.mdmdiff-added {
    background: #c8f0da;
}
/* .mdmreport-table .mdmreport-record.mdmdiff-added td { */
/*     padding-top: 1.2em; */
/* } */
/* .mdmreport-table .mdmreport-record.mdmdiff-added td:first-child:before { */
/*     content: ""added""; */
/*     display: block; */
/*     position: absolute; */
/*     padding-right: 0.5em; */
/*     top: 0; */
/*     padding-top: 0; */
/*     color: #090; */
/*     z-index: 999; */
/*     font-weight: 700; */
/*     font-size: 70%; */
/* } */
.mdmreport-table .mdmreport-record.mdmdiff-removed {
    background: #ffcbbd;
}
/* .mdmreport-table .mdmreport-record.mdmdiff-removed td { */
/*     padding-top: 1.2em; */
/* } */
/* .mdmreport-table .mdmreport-record.mdmdiff-removed td:first-child:before { */
/*     content: ""removed""; */
/*     display: block; */
/*     position: absolute; */
/*     padding-right: 0.5em; */
/*     top: 0; */
/*     padding-top: 0; */
/*     color: #b00; */
/*     z-index: 999; */
/*     font-weight: 700; */
/*     font-size: 70%; */
/* } */
.mdmreport-table .mdmreport-record.mdmdiff-ghost {
    background: #eeeeee;
    color: #444444;
}
.mdmreport-table .mdmreport-record.mdmdiff-diff {
    background: #ffe49c;
}
.mdmreport-table .mdmreport-record.mdmdiff-diff.mdmdiff-specialtype-routing, .mdmreport-table .mdmreport-record.mdmdiff-diff.mdmdiff-specialtype-routing:hover {
    background: #f2f2f2;
}
.mdmreport-prop-fieldvalue {
    color: #600060;
}

.mdmdiff-inlineoverlay-added { background: #6bc795; }
.mdmdiff-inlineoverlay-removed { background: #f59278; }
.mdmdiff-inlineoverlay-diff { background: #edbf45; }

.mdmreport-format-multiline {
    /* white-space: nowrap; */
    white-space: pre;
    white-space: pre;
}
.mdmreport-format-multiline br {
    display: none;
}
.mdmreport-format-hidden, .mdmreport-table .mdmreport-format-hidden {
    display: none;
}

/* controls */

.mdmreport-controls fieldset, fieldset.mdmreport-controls, .mdmreport-controls form, form.mdmreport-controls { display: block; border: none; margin: 0; padding: 0; }
.mdmreport-controls legend, .mdmreport-controls label {
    display: inline-block;
    line-height: 1em;
    padding: 0.35em;
    min-height: 1.3em;
}
.mdmreport-controls label {
    border: 1px solid transparent;
    transition: all 350ms ease;
}
.mdmreport-controls label:hover {
    border: 1px solid #ddd;
}
.mdmreport-controls label input[type="checkbox"] {
    display: inline-block;
    width: 0;
    margin-left: 1.35em;
    position: relative;
}
.mdmreport-controls label input[type="checkbox"]:before {
    content: " ";
    display: block;
    text-align: center;
    position: absolute;
    width: 1em;
    height: 1em;
    background: #fff;
    border: 1px solid #ddd;
    right: 100%;
    transform: translateX(-0.35em);
    line-height: .8em;
    padding: 0.1em 0 0.1em;
}
.mdmreport-controls label input[type="checkbox"]:checked:before {
    content: "\\002A09";
}
.mdmreport-controls-group input.mdmreport-controls[type="text"], .mdmreport-controls .mdmreport-controls-group input[type="text"] {
    display: block;
    line-height: 1em;
    padding: 0.35em;
    min-height: 1.3em;
    width: 100%;
    border: 1px solid #dddddd;
    border-radius: 0.18em;
}

.mdmreport-controls[disabled], .mdmreport-controls.disabled {
    position: relative;
}
.mdmreport-controls[disabled]:before, .mdmreport-controls.disabled:before {
    content: " ";
    display: block;
    position: absolute;
    left: 0; top: 0; right: 0; bottom: 0;
    background: rgba(224,224,224,0.55);
}
</style>

    """

TEMPLATE_HTML_SCRIPTS = """
<script>
(function() {
    function beautifyDates() {
        let errorBannerEl = null;
        try {
            errorBannerEl = document.querySelector('#error_banner');
            if( !errorBannerEl ) throw new Error('no error banner, stop execution of js scripts');
        } catch(e) {
            throw e;
            return;
        }
        try {
            const elements = document.querySelectorAll('[data-role="date"]');
            Array.prototype.forEach.call(elements,function(el) {
                const content = el.innerText||el.textContent;
                const dt = /[1-9]/.test(content) ? new Date(content) : undefined;
                // const result = dt ? `original: ${content}, converted: ${dt}` : content; // for debugging
                const result = dt ? `${dt}` : content;
                el.innerText = result;
            });
            document.removeEventListener('DOMContentLoaded',beautifyDates);
        } catch(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            try {
                document.removeEventListener('DOMContentLoaded',beautifyDates);
            } catch(ee) {}
            throw e;
        }
    }
    window.addEventListener('DOMContentLoaded',beautifyDates);
})()
</script>
<script>
(function() {
    function alignColWidths() {
        let errorBannerEl = null;
        try {
            errorBannerEl = document.querySelector('#error_banner');
            if( !errorBannerEl ) throw new Error('no error banner, stop execution of js scripts');
        } catch(e) {
            throw e;
            return;
        }
        try {
            const tables_all = document.querySelectorAll('.mdmreport-table');
            const cssSheet = new CSSStyleSheet();
            document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
            function process() {
                Array.prototype.forEach.call(tables_all,function(tableEl) {
                    tableEl.classList.remove('mdmreport-table-formatting-fixeddimensions');
                });
                cssSheet.replaceSync('');
                const colWidthsData = [];
                var colMaxIndex = 0;
                Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                    const rowElements = tableEl.querySelectorAll('tr.mdmreport-record');
                    if( rowElements.length>0 ) {
                        colElements = rowElements[0].querySelectorAll('tr.mdmreport-record>td');
                        Array.prototype.forEach.call(colElements,function(colEl,colIndex) {
                            if(!colWidthsData[colIndex]) colWidthsData[colIndex] = [];
                            colWidthsData[colIndex][tableIndex] = colEl.getBoundingClientRect().width;
                            if(colIndex>colMaxIndex) colMaxIndex = colIndex;
                        });
                    }
                });
                colWidthsAverage = [];
                for(let colIndex=0;colIndex<=colMaxIndex;++colIndex) {
                    var numCounted = 0;
                    Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                        const val = colWidthsData[colIndex][tableIndex];
                        const isValValid = isFinite(val) && (val>0);
                        if(isValValid) {
                            if(!colWidthsAverage[colIndex]) colWidthsAverage[colIndex] = 0;
                            colWidthsAverage[colIndex] += val;
                            numCounted++;
                        }
                    });
                    colWidthsAverage[colIndex] = colWidthsAverage[colIndex] / numCounted;
                    if(!(numCounted>0)) colWidthsAverage[colIndex] = 0;
                }
                var cssSyntax = '';
                for(colIndex=0;colIndex<=colMaxIndex;colIndex++) {
                    cssSyntax = cssSyntax + ' .mdmreport-colindex-'+colIndex+' { width: '+colWidthsAverage[colIndex]+'px; } ';
                }
                cssSheet.replaceSync(cssSyntax);
                Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                    //const rowElements = tableEl.querySelectorAll('tr.mdmreport-record');
                    //Array.prototype.forEach.call(rowElements,function(rowElement,tableIndex) {
                    //    colElements = rowElement.querySelectorAll('tr.mdmreport-record>td');
                    //    Array.prototype.forEach.call(colElements,function(colEl,colIndex) {
                    //        colEl.width = colWidthsAverage[colIndex];
                    //    });
                    //});
                    tableEl.classList.add('mdmreport-table-formatting-fixeddimensions');
                });
            };
            process();
            window.addEventListener('resize',process);
            document.removeEventListener('DOMContentLoaded',alignColWidths);
        } catch(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            try {
                document.removeEventListener('DOMContentLoaded',alignColWidths);
            } catch(ee) {}
            throw e;
        }
    }
    window.addEventListener('DOMContentLoaded',alignColWidths);
})()
</script>
<script>
(function() {
    function addControlBlock_ShowHideColumns() {
        let errorBannerEl = null;
        try {
            errorBannerEl = document.querySelector('#error_banner');
            if( !errorBannerEl ) throw new Error('no error banner, stop execution of js scripts');
        } catch(e) {
            throw e;
            return;
        }
        try {
            // 1. read data and find the list of columns in the report table
            const columns = [];
            const rowContainingColsElements = document.querySelectorAll('table.mdmreport-table tr.mdmreport-record');
            if(rowContainingColsElements.length>1) {
                const colElements = rowContainingColsElements[1].querySelectorAll('td.mdmreport-contentcell');
                Array.prototype.forEach.call(colElements,function(colEl) {
                    const cssClasses = Array.from(colEl.classList);
                    const cssClassesMatching = cssClasses.filter(function(n) {return /^\s*?(mdmreport-col-)(.*?)\s*?$/.test(n);});
                    cssClassesMatching.map(function(n) {return n.replace(/^\s*?(mdmreport-col-)(.*?)\s*?$/,'$2');}).forEach(function(colName) {
                        columns.push(colName);
                    });
                });
            };
            // 2. add a control block
            function initSettingCss() {
                // .mdmreport-hidecol-xxx .mdmreport-col-xxx
                const cssSheet = new CSSStyleSheet();
                const cssSyntax = columns.map(function(col) {
                    const colClassName = col.replace(/[^\w\-\.]/,'');
                    return ' .mdmreport-hidecol-xxx .mdmreport-col-xxx { display: none; } '.replaceAll('xxx',colClassName);
                }).join('');
                cssSheet.replaceSync(cssSyntax);
                document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
            }
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block to show/hide columns: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                    const bannerEl = document.createElement('div');
                    bannerEl.className = 'mdmreport-layout-plugin mdmreport-banner mdmreport-banner-columns';
                    bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Show/hide columns:</legend></div></fieldset></form>';
                    Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',function(event) {event.preventDefault();event.stopPropagation();return false;});});
                    pluginHolderEl.append(bannerEl);
                    columns.forEach(function(col) {
                        try {
                            const colText = col;
                            const colClassName = col.replace(/[^\w\-\.]/,'');
                            const labelEl = document.createElement('label');
                            labelEl.textContent = colText;
                            labelEl.classList.add('mdmreport-controls');
                            const checkboxEl = document.createElement('input');
                            checkboxEl.setAttribute('type','checkbox');
                            checkboxEl.setAttribute('checked','true');
                            checkboxEl.checked = true;
                            checkboxEl.addEventListener('change',function(event) {
                                const checkboxEl = event.target;
                                const className = `mdmreport-hidecol-${colClassName}`; // mdmreport-col-xxx
                                if( checkboxEl.checked ) {
                                    Array.prototype.forEach.call(document.querySelectorAll('table.mdmreport-table'),function(tableEl) {
                                        tableEl.classList.remove(className);
                                    });
                                } else {
                                    Array.prototype.forEach.call(document.querySelectorAll('table.mdmreport-table'),function(tableEl) {
                                        tableEl.classList.add(className);
                                    });
                                };
                            });
                            labelEl.prepend(checkboxEl);
                            bannerEl.querySelector('fieldset').append(labelEl);
                        } catch(e) {
                            try {
                                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
                            } catch(ee) {};
                            throw e;
                        }
                    });
            }
            initSettingCss();
            initAddingControlBlock();
            document.removeEventListener('DOMContentLoaded',addControlBlock_ShowHideColumns);
        } catch(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            try {
                document.removeEventListener('DOMContentLoaded',addControlBlock_ShowHideColumns);
            } catch(ee) {}
            throw e;
        }
    }
    window.addEventListener('DOMContentLoaded',addControlBlock_ShowHideColumns);
})()
</script>
"""

TEMPLATE_HTML_DIFF_SCRIPTS = ""

TEMPLATE_HTML_DIFF_STYLES = """
<style>
.mdmreportpage-type-MDDDiff-type-routingstandalone .mdmreport-record {
    display: none;
}
.mdmreportpage-type-MDDDiff-type-routingstandalone .mdmreport-record.mdmreport-record-type-routingline {
    display: table-row;
}
.mdmreportpage-type-MDDDiff-type-routingstandalone .mdmreport-record .mdmreport-contentcell {
    display: none;
}
.mdmreportpage-type-MDDDiff-type-routingstandalone .mdmreport-record .mdmreport-contentcell.mdmreport-cols-type-label {
    display: table-cell;
}
.mdmreportpage-type-MDDDiff-type-routingstandalone .mdmreport-layout-plugin {
    display: none;
}
</style>
    """

TEMPLATE_HTML_COPYBANNER = """
AP
    """

TEMPLATE_HTML_TABLE_BEGIN = """
<div class="wrapper mdmreport-table-wrapper mdmreport-wrapper-section-{{TABLE_ID}}">
<h3 class="mdmreport-table-title">Section {{TABLE_NAME}}</h3>
<table class="mdmreport-table mdmreport-table-section-{{TABLE_ID}}"><tbody>
"""

TEMPLATE_HTML_TABLE_END = """
</tbody></table></div>
"""

TEMPLATE_HTML_BEGIN = """

<!doctype html>
<html lang="">
<head>
      <meta charset="UTF-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width">
      <title>{{{{INS_TITLE}}}}</title>
      <style>{TEMPLATE_HTML_CSS_NORMALIZECSS}</style>
      <style>
      {TEMPLATE_HTML_STYLES}
      {TEMPLATE_HTML_STYLES_TABLE}
      </style>
      <script>window.reportType = '{{{{INS_REPORTTYPE}}}}';</script>
      {ADD_SCRIPTS}
</head>
<body class="mdmreportpage mdmreportpage-type-{{{{INS_REPORTTYPE}}}}">
<header class="header">
    <div class="container">
        <p>{{{{INS_REPORTTYPE}}}} Report</p>
    </div>
</header>
<div class="main">
    <div class="container">
        <h1>{{{{INS_HEADING}}}}</h1>
        <div class="mdmreport-banner mdmreport-banner-global">{{{{INS_BANNER}}}}</div>
        <div class="error error-banner" id="error_banner"></div>
        <div class="mdmreport-layout-plugin-placeholder" id="mdmreport_plugin_placeholder"></div><h2 style="display: none;">Sections</h2>
    """.format(
        TEMPLATE_HTML_CSS_NORMALIZECSS = TEMPLATE_HTML_CSS_NORMALIZECSS,
        TEMPLATE_HTML_STYLES = TEMPLATE_HTML_STYLES,
        TEMPLATE_HTML_STYLES_TABLE = TEMPLATE_HTML_STYLES_TABLE,
        ADD_SCRIPTS = '{allscripts}{diffstyles}{diffscripts}'.format(allscripts=TEMPLATE_HTML_SCRIPTS,diffscripts=TEMPLATE_HTML_DIFF_SCRIPTS,diffstyles=TEMPLATE_HTML_DIFF_STYLES),
        # INS_TITLE = fields_File_INS_TITLE,
        # INS_REPORTTYPE = fields_INS_REPORTTYPE,
        # INS_HEADING = fields_File_INS_HEADING,
        # INS_BANNER = ''.join( [ '<p>{content}</p>'.format(content=preptext_html(content)) for content in fields_File_ReportInfo ] )
    )

TEMPLATE_HTML_END = """
        </div>
    </div>
    <footer class="footer">
        <div class="container">{TEMPLATE_HTML_COPYBANNER}</div>
    </footer>
</body>
</html>
    """.format(
        TEMPLATE_HTML_COPYBANNER = TEMPLATE_HTML_COPYBANNER
    )
    
