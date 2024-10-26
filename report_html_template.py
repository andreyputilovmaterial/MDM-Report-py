
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
    * {
        box-sizing: border-box;
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
    font-size: 100%;
    border: 0.5px solid #666666;
    background: #e1e1e1;
    border-bottom: 4px solid #217346;
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

td.mdmreport-contentcell label {
    display: block;
    font-weight: 400;
    color: #666;
    font-size: 90%;
    padding: 0.25em 0 0.25em 1em;
    position: relative;
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
.mdmreport-sronly {
    visibility: hidden;
    display: block;
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0,0,0,0);
    border: 0;
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
                // first, clear out previous formatting
                Array.prototype.forEach.call(tables_all,function(tableEl) {
                    tableEl.classList.remove('mdmreport-table-formatting-fixeddimensions');
                });
                cssSheet.replaceSync('');
                // now find new width values
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
            // it's interesting, we don't care how many columns are there; we iterate over css classes, and adding show/hide functionality per css class
            // so, if 2 classes are added to a cell, there would be 2 checkboxes, and if there is a column missing necessary class, there would be no check box
            const columns = [];
            const columnTitles = {};
            const rowContainingColsElements = document.querySelectorAll('table.mdmreport-table tr.mdmreport-record');
            if(rowContainingColsElements.length>0) {
                const rowRefEl = rowContainingColsElements[0];
                const colElements = rowRefEl.querySelectorAll('td.mdmreport-contentcell');
                Array.prototype.forEach.call(colElements,function(colEl) {
                    const cssClasses = Array.from(colEl.classList);
                    const cssClassesMatching = cssClasses.filter(function(n) {return /^\\s*?(mdmreport-col-)(.*?)\\s*?$/ig.test(n);});
                    cssClassesMatching.map(function(n) {return n.replace(/^\\s*?(mdmreport-col-)(.*?)\\s*?$/ig,'$2');}).forEach(function(colNameFromCSS) {
                        const colName = colNameFromCSS;
                        //colName = colName.replace(/^\\s*/,'').replace(/\\s*$/,'');
                        const colTitlesAllOfThisCssClass = Array.from(rowRefEl.querySelectorAll(`.mdmreport-col-${colName}`)).map(el=>el.textContent);
                        const colTitlesNoDuplicates = colTitlesAllOfThisCssClass.reduce(function(acc,val){if(acc.includes(val))return acc; else return [...acc,val];},[]);
                        const colTitle = colTitlesNoDuplicates.length==1 ? colTitlesNoDuplicates[0] : `${colEl.textContent} (${colName})`;
                        columnTitles[colName] = colTitle;
                        columns.push(colName);
                    });
                });
            };
            // 2. add a control block
            function applyDefaultSetup(listOfControls) {
                try {
                    var listOfControlsShown = listOfControls;
                    const listOfControls_IncludesScripting = listOfControlsShown.filter(a=>a.id=='scripting');
                    const listOfControls_DoesNotIncludeScripting = listOfControlsShown.filter(a=>a.id!='scripting');
                    if( (listOfControls_IncludesScripting.length>0) && (listOfControls_DoesNotIncludeScripting.length>0) ) {
                        listOfControls_IncludesScripting.forEach(function(d){d.controlEl.checked=false;d.controlEl.dispatchEvent(new Event('change'));});
                        listOfControls_DoesNotIncludeScripting.forEach(function(d){d.controlEl.checked=true;d.controlEl.dispatchEvent(new Event('change'));});
                        listOfControlsShown = listOfControls_DoesNotIncludeScripting;
                    };
                    const listOfControls_IncludesLangcode = listOfControlsShown.filter(a=>/^\\s*?langcode.*?/ig.test(a.id));
                    const listOfControls_DoesNotIncludeLangcode = listOfControlsShown.filter(a=>!(/^\\s*?langcode.*?/ig.test(a.id)));
                    if( (listOfControls_IncludesLangcode.length>0) && (listOfControls_DoesNotIncludeLangcode.length>0) ) {
                        listOfControls_IncludesLangcode.forEach(function(d){d.controlEl.checked=false;d.controlEl.dispatchEvent(new Event('change'));});
                        listOfControls_DoesNotIncludeLangcode.forEach(function(d){d.controlEl.checked=true;d.controlEl.dispatchEvent(new Event('change'));});
                        listOfControlsShown = listOfControls_DoesNotIncludeLangcode;
                    };
                } catch(e) {
                    try {
                        errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
                    } catch(ee) {};
                    throw e;
                }
            }
            function initSettingCss() {
                // .mdmreport-hidecol-xxx .mdmreport-col-xxx
                const cssSheet = new CSSStyleSheet();
                const cssSyntax = columns.map(function(item) {
                    const itemClassName = item.replace(/[^\\w\\-\\.]/ig,'');
                    return ' .mdmreport-hidecol-xxx .mdmreport-col-xxx { display: none; } '.replaceAll('xxx',itemClassName);
                }).join('');
                cssSheet.replaceSync(cssSyntax);
                document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
            }
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block to show/hide columns: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                const bannerEl = document.createElement('div');
                bannerEl.className = 'mdmreport-showhidecolumns-plugin mdmreport-banner mdmreport-banner-columns';
                bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Show/hide columns:</legend></div></fieldset></form>';
                Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',function(event) {event.preventDefault();event.stopPropagation();return false;});});
                pluginHolderEl.append(bannerEl);
                controlsDefs = [];
                columns.forEach(function(col) {
                    try {
                        const colText = columnTitles[col];
                        const colClassName = col.replace(/[^\\w\\-\\.]/ig,'');
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
                        controlsDefs.push({id:colClassName,text:colText,controlEl:checkboxEl});
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
            setTimeout(function(){ applyDefaultSetup(controlsDefs); },50);
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
<script>
(function() {
    function addControlBlock_ShowHideSections() {
        let errorBannerEl = null;
        try {
            errorBannerEl = document.querySelector('#error_banner');
            if( !errorBannerEl ) throw new Error('no error banner, stop execution of js scripts');
        } catch(e) {
            throw e;
            return;
        }
        try {
            // 1. read data and find the list of sections in the report table
            sectionDefs = [];
            const sectionElements = document.querySelectorAll('[class^="mdmreport-wrapper-section-"], [class*=" mdmreport-wrapper-section-"]');
            Array.prototype.forEach.call(sectionElements,function(sectionElement) {
                var textTitle = `${(sectionElement.querySelector('h3') || {textContent:''}).textContent}`.replace(/^\\s*?section\\s+/ig,'');
                var textCss = ( Array.from(sectionElement.classList).filter(function(name){return /^\\s*?mdmreport-wrapper-section-/ig.test(name)}) || [''] )[0].replace(/^\\s*?mdmreport-wrapper-section-/ig,'');
                textTitle = textTitle.replace(/^\\s*(.*?)\\s*$/ig,'$1'); // trim
                textCss = textCss.replace(/^\\s*(.*?)\\s*$/ig,'$1'); // trim
                if( ( !!textTitle && (textTitle.length>0) ) || ( !!textCss && (textCss.length>0) ) ) {
                    if( !textTitle || (textTitle.length==0) ) textTitle = textCss;
                    if( !textCss || (textCss.length==0) ) textCss = textTitle;
                    textCss = textCss.replace(/[^\\w\\-\\.]/ig,'-');
                    sectionDefs.push({text:textTitle,id:textCss});
                }
            });
            // 2. add a control block
            function applyDefaultSetup(listOfControls) {
                if(listOfControls.map(a=>a.id).includes('fields')) {
                    listOfControls.filter(a=>a.id=='fields').forEach(function(d){d.controlEl.checked=true;d.controlEl.dispatchEvent(new Event('change'));});
                    listOfControls.filter(a=>a.id!='fields').forEach(function(d){d.controlEl.checked=false;d.controlEl.dispatchEvent(new Event('change'));});
                };
            }
            function initSettingCss() {
                const cssSheet = new CSSStyleSheet();
                const cssSyntax = sectionDefs.map(function(item) {
                    const itemClassName = item['id'].replace(/[^\\w\\-\\.]/,'');
                    return ' .mdmreport-hidesection-xxx .mdmreport-wrapper-section-xxx { display: none; } '.replaceAll('xxx',itemClassName);
                }).join('');
                cssSheet.replaceSync(cssSyntax);
                document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
            }
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block to show/hide sections: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                const bannerEl = document.createElement('div');
                bannerEl.className = 'mdmreport-showhidesections-plugin mdmreport-banner mdmreport-banner-sections';
                bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Show/hide sections:</legend></div></fieldset></form>';
                Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',function(event) {event.preventDefault();event.stopPropagation();return false;});});
                pluginHolderEl.append(bannerEl);
                const controlsDefs = [];
                sectionDefs.forEach(function(sectionDef) {
                    try {
                        const colText = sectionDef['text'];
                        const colClassName = sectionDef['id'];
                        const labelEl = document.createElement('label');
                        labelEl.textContent = colText;
                        labelEl.classList.add('mdmreport-controls');
                        const checkboxEl = document.createElement('input');
                        checkboxEl.setAttribute('type','checkbox');
                        checkboxEl.setAttribute('checked','true');
                        checkboxEl.checked = true;
                        checkboxEl.addEventListener('change',function(event) {
                            const checkboxEl = event.target;
                            const className = `mdmreport-hidesection-${colClassName}`;
                            if( checkboxEl.checked ) {
                                Array.prototype.forEach.call(document.querySelectorAll('.mdmreportpage'),function(tableEl) {
                                    tableEl.classList.remove(className);
                                });
                            } else {
                                Array.prototype.forEach.call(document.querySelectorAll('.mdmreportpage'),function(tableEl) {
                                    tableEl.classList.add(className);
                                });
                            };
                        });
                        labelEl.prepend(checkboxEl);
                        bannerEl.querySelector('fieldset').append(labelEl);
                        controlsDefs.push({id:sectionDef['id'],text:colText,controlEl:checkboxEl});
                    } catch(e) {
                        try {
                            errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
                        } catch(ee) {};
                        throw e;
                    }
                });
                setTimeout(function(){ applyDefaultSetup(controlsDefs); },50);
            }
            initSettingCss();
            initAddingControlBlock();
            document.removeEventListener('DOMContentLoaded',addControlBlock_ShowHideSections);
        } catch(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            try {
                document.removeEventListener('DOMContentLoaded',addControlBlock_ShowHideSections);
            } catch(ee) {}
            throw e;
        }
    }
    window.addEventListener('DOMContentLoaded',addControlBlock_ShowHideSections);
})()
</script>
<style>
.mdmreport-record.mdmreport-tablefilterplugin-hide-0, .mdmreport-record.mdmreport-tablefilterplugin-hide-1, .mdmreport-record.mdmreport-tablefilterplugin-hide-2, .mdmreport-record.mdmreport-tablefilterplugin-hide-3, .mdmreport-record.mdmreport-tablefilterplugin-hide-4, .mdmreport-record.mdmreport-tablefilterplugin-hide-5, .mdmreport-record.mdmreport-tablefilterplugin-hide-6, .mdmreport-record.mdmreport-tablefilterplugin-hide-7, .mdmreport-record.mdmreport-tablefilterplugin-hide-8, .mdmreport-record.mdmreport-tablefilterplugin-hide-9, .mdmreport-record.mdmreport-tablefilterplugin-hide-10, .mdmreport-record.mdmreport-tablefilterplugin-hide-11, .mdmreport-record.mdmreport-tablefilterplugin-hide-12, .mdmreport-record.mdmreport-tablefilterplugin-hide-13, .mdmreport-record.mdmreport-tablefilterplugin-hide-14, .mdmreport-record.mdmreport-tablefilterplugin-hide-15, .mdmreport-record.mdmreport-tablefilterplugin-hide-16, .mdmreport-record.mdmreport-tablefilterplugin-hide-17, .mdmreport-record.mdmreport-tablefilterplugin-hide-18, .mdmreport-record.mdmreport-tablefilterplugin-hide-19, .mdmreport-record.mdmreport-tablefilterplugin-hide-20, .mdmreport-record.mdmreport-tablefilterplugin-hide-21, .mdmreport-record.mdmreport-tablefilterplugin-hide-22, .mdmreport-record.mdmreport-tablefilterplugin-hide-23, .mdmreport-record.mdmreport-tablefilterplugin-hide-24, .mdmreport-record.mdmreport-tablefilterplugin-hide-25, .mdmreport-record.mdmreport-tablefilterplugin-hide-26, .mdmreport-record.mdmreport-tablefilterplugin-hide-27, .mdmreport-record.mdmreport-tablefilterplugin-hide-28, .mdmreport-record.mdmreport-tablefilterplugin-hide-29, .mdmreport-record.mdmreport-tablefilterplugin-hide-30, .mdmreport-record.mdmreport-tablefilterplugin-hide-31, .mdmreport-record.mdmreport-tablefilterplugin-hide-32, .mdmreport-record.mdmreport-tablefilterplugin-hide-33, .mdmreport-record.mdmreport-tablefilterplugin-hide-34, .mdmreport-record.mdmreport-tablefilterplugin-hide-35, .mdmreport-record.mdmreport-tablefilterplugin-hide-36, .mdmreport-record.mdmreport-tablefilterplugin-hide-37, .mdmreport-record.mdmreport-tablefilterplugin-hide-38, .mdmreport-record.mdmreport-tablefilterplugin-hide-39, .mdmreport-record.mdmreport-tablefilterplugin-hide-40, .mdmreport-record.mdmreport-tablefilterplugin-hide-41, .mdmreport-record.mdmreport-tablefilterplugin-hide-42, .mdmreport-record.mdmreport-tablefilterplugin-hide-43, .mdmreport-record.mdmreport-tablefilterplugin-hide-44, .mdmreport-record.mdmreport-tablefilterplugin-hide-45, .mdmreport-record.mdmreport-tablefilterplugin-hide-46, .mdmreport-record.mdmreport-tablefilterplugin-hide-47, .mdmreport-record.mdmreport-tablefilterplugin-hide-48, .mdmreport-record.mdmreport-tablefilterplugin-hide-49, .mdmreport-record.mdmreport-tablefilterplugin-hide-50, .mdmreport-record.mdmreport-tablefilterplugin-hide-51, .mdmreport-record.mdmreport-tablefilterplugin-hide-52, .mdmreport-record.mdmreport-tablefilterplugin-hide-53, .mdmreport-record.mdmreport-tablefilterplugin-hide-54, .mdmreport-record.mdmreport-tablefilterplugin-hide-55, .mdmreport-record.mdmreport-tablefilterplugin-hide-56, .mdmreport-record.mdmreport-tablefilterplugin-hide-57, .mdmreport-record.mdmreport-tablefilterplugin-hide-58, .mdmreport-record.mdmreport-tablefilterplugin-hide-59, .mdmreport-record.mdmreport-tablefilterplugin-hide-60, .mdmreport-record.mdmreport-tablefilterplugin-hide-61, .mdmreport-record.mdmreport-tablefilterplugin-hide-62, .mdmreport-record.mdmreport-tablefilterplugin-hide-63, .mdmreport-record.mdmreport-tablefilterplugin-hide-64, .mdmreport-record.mdmreport-tablefilterplugin-hide-65, .mdmreport-record.mdmreport-tablefilterplugin-hide-66, .mdmreport-record.mdmreport-tablefilterplugin-hide-67, .mdmreport-record.mdmreport-tablefilterplugin-hide-68, .mdmreport-record.mdmreport-tablefilterplugin-hide-69, .mdmreport-record.mdmreport-tablefilterplugin-hide-70, .mdmreport-record.mdmreport-tablefilterplugin-hide-71, .mdmreport-record.mdmreport-tablefilterplugin-hide-72, .mdmreport-record.mdmreport-tablefilterplugin-hide-73, .mdmreport-record.mdmreport-tablefilterplugin-hide-74, .mdmreport-record.mdmreport-tablefilterplugin-hide-75, .mdmreport-record.mdmreport-tablefilterplugin-hide-76, .mdmreport-record.mdmreport-tablefilterplugin-hide-77, .mdmreport-record.mdmreport-tablefilterplugin-hide-78, .mdmreport-record.mdmreport-tablefilterplugin-hide-79, .mdmreport-record.mdmreport-tablefilterplugin-hide-80, .mdmreport-record.mdmreport-tablefilterplugin-hide-81, .mdmreport-record.mdmreport-tablefilterplugin-hide-82, .mdmreport-record.mdmreport-tablefilterplugin-hide-83, .mdmreport-record.mdmreport-tablefilterplugin-hide-84, .mdmreport-record.mdmreport-tablefilterplugin-hide-85, .mdmreport-record.mdmreport-tablefilterplugin-hide-86, .mdmreport-record.mdmreport-tablefilterplugin-hide-87, .mdmreport-record.mdmreport-tablefilterplugin-hide-88, .mdmreport-record.mdmreport-tablefilterplugin-hide-89, .mdmreport-record.mdmreport-tablefilterplugin-hide-90, .mdmreport-record.mdmreport-tablefilterplugin-hide-91, .mdmreport-record.mdmreport-tablefilterplugin-hide-92, .mdmreport-record.mdmreport-tablefilterplugin-hide-93, .mdmreport-record.mdmreport-tablefilterplugin-hide-94, .mdmreport-record.mdmreport-tablefilterplugin-hide-95, .mdmreport-record.mdmreport-tablefilterplugin-hide-96, .mdmreport-record.mdmreport-tablefilterplugin-hide-97, .mdmreport-record.mdmreport-tablefilterplugin-hide-98, .mdmreport-record.mdmreport-tablefilterplugin-hide-99 {
    display: none!important;
}
tr.mdmreport-record td.mdmreport-contentcell.mdmreport-tablefilterplugin-enchancedcell {
    padding-bottom: 2.55em;
    position: relative;
}
td.mdmreport-contentcell .mdmreport-tablefilterplugin-controls {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 2px; /* to align with that green bottom border */
    /* height: 1.9em; */
    padding: 0; /* .1em; */
    /* line-height: 1em;
    padding: 0.35em; */
}
</style>
<script>
(function() {
    function addElementsToTables_TableFilters() {
        let errorBannerEl = null;
        try {
            errorBannerEl = document.querySelector('#error_banner');
            if( !errorBannerEl ) throw new Error('no error banner, stop execution of js scripts');
        } catch(e) {
            throw e;
            return;
        }
        function bubbleException(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            throw e;
        }
        try {
            // 1. read data and find the list of sections in the report table
            const sectionElements = document.querySelectorAll('[class^="mdmreport-wrapper-section-"], [class*=" mdmreport-wrapper-section-"]');
            Array.prototype.forEach.call(sectionElements,function(sectionElement) {
                var textTitle = `${(sectionElement.querySelector('h3') || {textContent:''}).textContent}`.replace(/^\\s*?section\\s+/ig,'');
                const sectionClasses = Array.from(sectionElement.classList).filter(function(name){return /^\\s*?mdmreport-wrapper-section-/ig.test(name)});
                const sectionClassesUnique = sectionClasses.filter(function(className){return document.querySelectorAll('.'+className).length==1});
                if( !(sectionClassesUnique.length>0) ) return;
                const sectionClass = sectionClassesUnique[0];
                var textCss = sectionClass.replace(/^\\s*?mdmreport-wrapper-section-/ig,'');
                textTitle = textTitle.replace(/^\\s*(.*?)\\s*$/ig,'$1'); // trim
                textCss = textCss.replace(/^\\s*(.*?)\\s*$/ig,'$1'); // trim
                if( !( ( !!textTitle && (textTitle.length>0) ) || ( !!textCss && (textCss.length>0) ) ) ) return;
                if( !textTitle || (textTitle.length==0) ) textTitle = textCss;
                if( !textCss || (textCss.length==0) ) textCss = textTitle;
                textCss = textCss.replace(/[^\\w\\-\\.]/ig,'-');
                const sectionDef = {
                    text:textTitle,
                    id:textCss,
                    tableElement:sectionElement.querySelector('table.mdmreport-table'),
                    sectionClass: sectionClass
                    };
                if(!sectionDef.tableElement) return;
                const headerRowEls = sectionDef.tableElement.querySelectorAll('tr.mdmreport-record-header');
                const allRows = Array.from(sectionDef.tableElement.querySelectorAll('tr.mdmreport-record:not(.mdmreport-record-header)')).map(function(element,index) {
                    const texts = Array.from(element.querySelectorAll('td.mdmreport-contentcell')).map(function(el){return  el.innerText||el.textContent});
                    return {element,texts,index};
                });
                if(!(headerRowEls.length>0)) return;
                const headerRowEl = headerRowEls[0];
                const cellElements = headerRowEl.querySelectorAll('td.mdmreport-contentcell');
                Array.from(cellElements).forEach(function(cellEl,colIndex){
                    const controlGroupElAdd = document.createElement('div');
                    controlGroupElAdd.className = 'mdmreport-tablefilterplugin-controls';
                    controlGroupElAdd.innerHTML = '<fieldset class="mdmreport-controls"><div class="mdmreport-controls-group"><input type="text" value="" placeholder="type something to filter..." /></div></fieldset>';
                    const controlEl = controlGroupElAdd.querySelector('input');
                    function doFilter() {
                        const checkStr = controlEl.value;
                        allRows.forEach(function(rowDef) {
                            const cellContents = rowDef.texts[colIndex];
                            const isMatching = (checkStr.length==0) || cellContents.toLowerCase().includes(checkStr.toLowerCase());
                            const cssControlClass = `mdmreport-tablefilterplugin-hide-${colIndex}`;
                            if(isMatching)
                                rowDef.element.classList.remove(cssControlClass);
                            else
                                rowDef.element.classList.add(cssControlClass);
                        });
                    }
                    const promiseState = {
                        active: false
                    };
                    function doFilterDelayed() {
                        if(promiseState.active) {
                            // just keep going
                        } else {
                            promiseState.active = true;
                            const promise = new Promise(function(resolve,reject){setTimeout(resolve,100);});
                            promise.then(function() {
                                try {
                                    promiseState.active = false;
                                    doFilter();
                                } catch(e) {
                                    bubbleException(e);
                                    throw e;
                                }
                            });
                        }
                    }
                    function handleChange(event) {
                        try {
                            //event.preventDefault();
                            //event.stopPropagation();
                            doFilterDelayed();
                            //return false;
                        } catch(e) {
                            bubbleException(e);
                            throw e;
                        }
                    }
                    controlEl.addEventListener('change',handleChange);
                    controlEl.addEventListener('keyup',handleChange);
                    controlEl.addEventListener('keydown',handleChange);
                    controlEl.addEventListener('keypress',handleChange);
                    cellEl.append(controlGroupElAdd);
                    cellEl.classList.add('mdmreport-tablefilterplugin-enchancedcell');
                });
            });
        } catch(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            throw e;
        }
    }
    function addControlBlock_TableFilters() {
        let errorBannerEl = null;
        try {
            errorBannerEl = document.querySelector('#error_banner');
            if( !errorBannerEl ) throw new Error('no error banner, stop execution of js scripts');
        } catch(e) {
            throw e;
            return;
        }
        try {
            // 2. add a control block
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block with table filters: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                const bannerEl = document.createElement('div');
                bannerEl.className = 'mdmreport-tablefilters-plugin mdmreport-banner mdmreport-banner-tablefilters';
                bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Add the ability to filter tables by content</legend></div><input type="submit" value="Yes, add this please!" /></fieldset></form>';
                Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',function(event) {
                    try {
                        event.preventDefault();
                        event.stopPropagation();
                        addElementsToTables_TableFilters();
                        //bannerEl.classList.add('mdmreport-format-hidden');
                        bannerEl.innerHTML = '<p>Add the ability to filter tables by content</p><span>Done, input boxes are added below the header line in every table.</span>';
                        return false;
                    } catch(e) {
                        try {
                            errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
                        } catch(ee) {};
                        throw e;
                    }
                });});
                pluginHolderEl.append(bannerEl);
            }
            initAddingControlBlock();
            document.removeEventListener('DOMContentLoaded',addControlBlock_TableFilters);
        } catch(e) {
            try {
                errorBannerEl.innerHTML = errorBannerEl.innerHTML + `Error: ${e}<br />`;
            } catch(ee) {};
            try {
                document.removeEventListener('DOMContentLoaded',addControlBlock_TableFilters);
            } catch(ee) {}
            throw e;
        }
    }
    window.addEventListener('DOMContentLoaded',addControlBlock_TableFilters);
})()
</script>
"""

TEMPLATE_HTML_DIFF_SCRIPTS = ""

TEMPLATE_HTML_DIFF_STYLES = """
<style>
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
        <p>{{{{INS_PAGEHEADER}}}}</p>
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
    
