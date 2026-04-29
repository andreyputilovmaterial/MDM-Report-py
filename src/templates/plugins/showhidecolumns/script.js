

    /* === show/hide columns js === */

    const globalDataStored = {};

    const cssSheet = new CSSStyleSheet();

    function decideColumnsShownAtStartup(columnIDs,addedData) {
        function normalizeSectionId(id) {
            return id.replace(/_/ig,' ').replace(/\s/ig,' ').replace(/\bx\d+\b/ig,' ').replace(/\s+/ig,' ').replace(/^\s*/ig,'').replace(/\s*$/ig,'');
        }
        const columnAll = new Set(columnIDs);
        let columns = new Set(columnAll);
        if(Array.from(columns).length==0) {
            return Array.from(columns);
        }
        const sectionNames = addedData.sectionNames.map(normalizeSectionId)
        function setDifference(a,b){/* something is not working with Sets in my chrome, strange - adding this helper fn to find differences as between arrays */  return new Set(Array.from(a).filter(function(ai){return !Array.from(b).includes(ai);})); }
        const columns_subsetName = new Set(columnIDs.filter(function(id){return /^\s*?name\s*?$/.test(id)}));
        const columns_subsetFlag = new Set(columnIDs.filter(function(id){return /^\s*?flag.*\s*?$/.test(id)}));
        const columns_subsetLabel = new Set(columnIDs.filter(function(id){return /^\s*?label\w*\s*?$/.test(id)}));
        const columns_subsetProperties = new Set(columnIDs.filter(function(id){return /^\s*?properties\w*\s*?$/.test(id)}));
        const columns_subsetAttributes = new Set(columnIDs.filter(function(id){return /^\s*?attributes\w*\s*?$/.test(id)}));
        const columns_subsetTranslations = new Set(columnIDs.filter(function(id){return /^\s*?langcode.*\s*?$/.test(id)}));
        const columns_subsetScripting = new Set(columnIDs.filter(function(id){return /^\s*?script\w*\s*?$/.test(id)}));
        const columns_subsetRawText = new Set(columnIDs.filter(function(id){return /^\s*?rawtext\w*\s*?$/.test(id)}));
        /* if diff on diffs */
        if( (columns_subsetFlag.size>1) && columns_subsetFlag.has('flagdiff') ) {
            const columns_subsetUnimportantFlagsToHide = setDifference(columns_subsetFlag,new Set(['flagdiff']));
            columns = setDifference(columns,columns_subsetUnimportantFlagsToHide);
        }
        /* if "routing" is the only section shown */
        if( ( (Array.from(sectionNames)).includes('routing') ) && ( Array.from(setDifference(sectionNames,['routing']))==0 ) ) {
            if(Array.from(columns_subsetLabel).length>0) {
                return Array.from(columns_subsetLabel);
            }
        }
        /* if layout represents diff in text files, comparing raw contents */
        if( ( Array.from(sectionNames).length==1 ) && ( Array.from(columns_subsetRawText).length>0 ) ) {
            if(Array.from(columns_subsetRawText).length>0) {
                const statisticsNumRows = (function(){
                    const sectionsMatching = addedData.sectionDefs.filter(()=>true);
                    if(sectionsMatching.length==1) {
                        const section = sectionsMatching[0];
                        const statisticsText = !!section.statisticsText ? section.statisticsText : '';
                        if(!!statisticsText && statisticsText.trim().length>0 ) {
                            const matches = Array.from(statisticsText.matchAll( /\brows\b\s*?\btotal\s*?:\s*?(\d+)\b,/ig ));
                            if( matches.length>0 ) {
                                const resultTxt = matches[0][1];
                                return +resultTxt;
                            }
                        }
                    } /* else return NaN */;
                    return NaN;
                })();
                if( isFinite(statisticsNumRows) && statisticsNumRows==1 ) {
                    return Array.from(columns_subsetRawText);
                } else {
                    return [...columns_subsetFlag,...columns_subsetRawText];
                }
            }
        }
        /* if scheme is representing excel file, hide clunky "row name" column */
        if( ((addedData.columnDefs.filter(a=>(a.id=='name')&&(a.text=='Row unique indentifier'))).length>0) && ((addedData.columnDefs.filter(a=>(/^\s*?axis\s*?\(\s*?side\s*?\).*?/.test(a.text)))).length>0) ) {
            return Array.from(setDifference( columns, columns_subsetName ))
        }
        /* if likely a MDD, hide translationoverlays columns */
        if( (addedData.sectionDefs.map(a=>a.text).filter(a=>(/.*?(?:shared[_\s]+list|(?:\bfield(?:s)?\b)).*?/.test(a))).length>0) && ( (Array.from(columns_subsetName)).length>0 ) && ( (Array.from(columns_subsetLabel)).length>0 ) ) {
            const result_TranslationsExcluded = setDifference( columns, columns_subsetTranslations )
            if(Array.from(result_TranslationsExcluded).length>0) {
                const result_ScriptingTranslationsExcluded = setDifference( result_TranslationsExcluded, columns_subsetScripting )
                if(Array.from(result_ScriptingTranslationsExcluded).length>0) {
                    return Array.from(result_ScriptingTranslationsExcluded);
                } else {
                    return Array.from(result_TranslationsExcluded);
                }
            }
        }
        return Array.from(columns);
    }

    function addControlBlock_ShowHideColumns() {
        try {
            // 1. read data and find the list of columns in the report table
            // it's interesting, we don't care how many columns are there; we iterate over css classes, and adding show/hide functionality per css class
            // so, if 2 classes are added to a cell, there would be 2 checkboxes, and if there is a column missing necessary class, there would be no check box
            const columns = [];
            const columnTitles = {};
            const sectionEls = document.querySelectorAll('table.mdmreport-table');
            Array.from(sectionEls).forEach(function(sectionEl){
                const rowContainingColsElements = sectionEl.querySelectorAll('tr.mdmreport-record');
                Array.from(rowContainingColsElements).filter(function(e,i){return i==0;}).forEach(function(rowRefEl){
                    const colElements = rowRefEl.querySelectorAll('td.mdmreport-contentcell');
                    Array.prototype.forEach.call(colElements,function(colEl) {
                        const cssClasses = Array.from(colEl.classList);
                        const cssClassesMatching = cssClasses.filter(function(n) {return /^\s*?(mdmreport-col-)(.*?)\s*?$/ig.test(n);});
                        cssClassesMatching.map(function(n) {return n.replace(/^\s*?(mdmreport-col-)(.*?)\s*?$/ig,'$2');}).forEach(function(colNameFromCSS) {
                            const colName = colNameFromCSS;
                            //colName = colName.replace(/^\s*/,'').replace(/\s*$/,'');
                            const colTitlesAllOfThisCssClass = Array.from(rowRefEl.querySelectorAll(`.mdmreport-col-${colName}`)).map(el=>el.textContent);
                            const colTitlesNoDuplicates = colTitlesAllOfThisCssClass.reduce(function(acc,val){if(acc.includes(val))return acc; else return [...acc,val];},[]);
                            const colTitle = colTitlesNoDuplicates.length==1 ? colTitlesNoDuplicates[0] : `${colEl.textContent} (${colName})`;
                            if( columns.includes(colName) ) {
                                /* skip - already on the list */
                            } else {
                                columnTitles[colName] = colTitle;
                                columns.push(colName);
                            }
                        });
                    });
                });
            });
            // 2. add a control block
            function applyDefaultSetup(listOfControls) {
                // input: array of {id:colClassName,text:colText,controlEl:checkboxEl}
                // expected behaviour: check/uncheck listOfControls[..].controlEl
                // not a clean fn
                try {
                    columnsAll = listOfControls.map(function(a){return a.id});
                    const sectionElements = document.querySelectorAll('[class^="mdmreport-wrapper-section-"], [class*=" mdmreport-wrapper-section-"]');
                    const sectionDefs = Array.from(sectionElements).map(function(sectionElement){
                        var textTitle = `${(sectionElement.querySelector('h3') || {textContent:''}).textContent}`.replace(/^\s*?section\s+/ig,'');
                        var textCss = ( Array.from(sectionElement.classList).filter(function(name){return /^\s*?mdmreport-wrapper-section-/ig.test(name)}) || [''] )[0].replace(/^\s*?mdmreport-wrapper-section-/ig,'');
                        textTitle = textTitle.replace(/^\s*(.*?)\s*$/ig,'$1');
                        /* trim */ textCss = textCss.replace(/^\s*(.*?)\s*$/ig,'$1');
                        /* trim */ if( ( !!textTitle && (textTitle.length>0) ) || ( !!textCss && (textCss.length>0) ) ) {
                            if( !textTitle || (textTitle.length==0) ) textTitle = textCss;
                            if( !textCss || (textCss.length==0) ) textCss = textTitle; textCss = textCss.replace(/[^\w\-\.]/ig,'-');
                        }
                        const statisticsEl = sectionElement.querySelector('.mdmreport-banner-table-details-statistics');
                        const statisticsText = !!statisticsEl && (`${statisticsEl.innerText}`.trim().length>0) ? `${statisticsEl.innerText}`.trim() : null;
                        return {
                            text: textTitle,
                            id: textCss,
                            name: textCss,
                            statisticsText: statisticsText,
                            el: sectionElement
                        };
                    });
                    const meta = [];
                    const addedData = {
                        columnDefs: listOfControls,
                        sectionNames: sectionDefs.map(a=>a.name),
                        sectionDefs: sectionDefs,
                        meta: meta
                    };
                    columnsShown = decideColumnsShownAtStartup(columnsAll,addedData).filter( hid => (!Object.keys(globalDataStored).includes(hid) || (Object.keys(globalDataStored).filter(id=>!!globalDataStored[id]).includes(hid)) ) ).concat( Object.keys(globalDataStored).filter(id=>!!globalDataStored[id]) );
                    columnsAll.forEach(function(columnId){
                        const d = listOfControls.filter(function(def){ return def.id==columnId; })[0];
                        const isShown = columnsShown.includes(columnId);
                        if( isShown ) {
                            d.controlEl.checked = true;
                            d.controlEl.dispatchEvent(new Event('change'));
                        } else {
                            d.controlEl.checked = false;
                            d.controlEl.dispatchEvent(new Event('change'));
                        }
                    });
                } catch(e) {
                    printErrors(e);
                    throw e;
                }
            }
            function initSettingCss() {
                // .mdmreport-hidecol-xxx .mdmreport-col-xxx
                const cssSyntax = columns.map(function(item) {
                    const itemClassName = item.replace(/[^\w\-\.]/ig,'');
                    return ' .mdmreport-hidecol-xxx .mdmreport-col-xxx { display: none; } '.replaceAll('xxx',itemClassName);
                }).join('');
                cssSheet.replaceSync(cssSyntax);
                document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
            }
            const dispatchResizeEventData = {
                promise: null
            };
            function dispatchResizeEvent() {
                if(!!dispatchResizeEventData.promise) {
                    /* setTimeout(resolve,40); */
                } else {
                    dispatchResizeEventData.promise = new Promise((resolve,reject)=>{
                        setTimeout(resolve,40);
                    });
                    dispatchResizeEventData.promise.then(()=>{
                        window.dispatchEvent(new Event('resize'));
                        dispatchResizeEventData.promise = null;
                    });
                }
            }
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block to show/hide columns: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                const bannerEl = document.createElement('div');
                bannerEl.className = 'mdmreport-showhidecolumns-plugin mdmreport-banner mdmreport-banner-columns';
                bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Show/hide columns:</legend></div></fieldset></form>';
                Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',wrapErrors(function(event) {event.preventDefault();event.stopPropagation();return false;}));});
                const possiblyExistingEl = document.querySelector('.mdmreport-showhidecolumns-plugin');
                if( possiblyExistingEl ) {
                    possiblyExistingEl.replaceWith(bannerEl);
                } else {
                    pluginHolderEl.append(bannerEl);
                }
                controlsDefs = [];
                columns.forEach(function(col) {
                    try {
                        const colText = columnTitles[col];
                        const colClassName = col.replace(/[^\w\-\.]/ig,'');
                        const labelEl = document.createElement('label');
                        labelEl.textContent = colText;
                        labelEl.classList.add('mdmreport-controls');
                        const checkboxEl = document.createElement('input');
                        checkboxEl.setAttribute('type','checkbox');
                        checkboxEl.setAttribute('checked','true');
                        checkboxEl.checked = true;
                        checkboxEl.addEventListener('change',wrapErrors(function(event) {
                            const checkboxEl = event.target;
                            const className = `mdmreport-hidecol-${colClassName}`; // mdmreport-col-xxx
                            globalDataStored[colClassName] = !!checkboxEl.checked;
                            if( checkboxEl.checked ) {
                                Array.prototype.forEach.call(document.querySelectorAll('table.mdmreport-table'),function(tableEl) {
                                    tableEl.classList.remove(className);
                                });
                            } else {
                                Array.prototype.forEach.call(document.querySelectorAll('table.mdmreport-table'),function(tableEl) {
                                    tableEl.classList.add(className);
                                });
                            };
                            dispatchResizeEvent();
                        }));
                        labelEl.prepend(checkboxEl);
                        bannerEl.querySelector('fieldset').append(labelEl);
                        controlsDefs.push({id:colClassName,text:colText,controlEl:checkboxEl});
                    } catch(e) {
                        printErrors(e);
                        throw e;
                    }
                });
            }
            initSettingCss();
            initAddingControlBlock();
            setTimeout(function(){ applyDefaultSetup(controlsDefs); },50);
            document.removeEventListener('DOMContentLoaded',addControlBlock_ShowHideColumns);
        } catch(e) {
            printErrors(e);
            throw e;
        }
    }

window.addEventListener('mdmdocument',wrapErrors(addControlBlock_ShowHideColumns));
window.addEventListener('mdmtable',wrapErrors(addControlBlock_ShowHideColumns));
