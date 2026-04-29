
    /* === show/hide sections js === */

    function addControlBlock_ShowHideSections() {
        try {
            function applyDefaultSetup(listOfControls) {
                function findListOfSectionsToShow(listOfControls,mode) {
                    if( mode=='mdd') {
                        const active = listOfControls.map(a=>a.id).includes('fields');
                        if( active ) {
                            return Array.from(listOfControls.filter(a=>a.id=='fields'));
                        } else {
                            return Arra.from(listOfControls);
                        };
                    } else if( mode=='diff' ) {
                        const defs = listOfControls.map(function(def) {
                            result = {...def};
                            const secDef = def['sectionDefRef'];
                            const detectDiffingStatus = {
                                indicatesSomething: false,
                                indicatesTrue: false,
                                indicatesFalse: false
                            };
                            if(!!secDef['statisticsText']) {
                                statisticsText = secDef['statisticsText'].replace(/\n/ig,' ');
                                /* looking for: "rows changed: 0" */
                                if( /\brows changed\s*?[=:]\s*?["']?\s*?([1-9,0]+)\s*?['"]?/ig.test(statisticsText) ) {
                                    const numChanged = +statisticsText.replace(/^.*?\brows changed\s*?[=:]\s*?["']?\s*?(\d+)\s*?['"]?.*?$/ig,'$1');
                                    if(numChanged>0) {
                                        detectDiffingStatus.indicatesTrue = true;
                                        detectDiffingStatus.indicatesFalse = false;
                                    } else {
                                        detectDiffingStatus.indicatesTrue = false;
                                        detectDiffingStatus.indicatesFalse = true;
                                    }
                                }
                                /* looking for: "something changed: false" */
                                if( /\bsomething changed\s*?[=:]\s*?["']?\s*?((?:true)|(?:false))\s*?['"]?/ig.test(statisticsText) ) {
                                    if( /\bsomething changed\s*?[=:]\s*?["']?\s*?((?:true))\s*?['"]?/ig.test(statisticsText) ) {
                                        detectDiffingStatus.indicatesTrue = true;
                                        detectDiffingStatus.indicatesFalse = false;
                                    } else if( /\bsomething changed\s*?[=:]\s*?["']?\s*?((?:false))\s*?['"]?/ig.test(statisticsText) ) {
                                        detectDiffingStatus.indicatesTrue = false;
                                        detectDiffingStatus.indicatesFalse = true;
                                    }
                                }
                                detectDiffingStatus.indicatesSomething = detectDiffingStatus.indicatesTrue || detectDiffingStatus.indicatesFalse || /(?:(?:something changed)|(?:rows changed\s*?[:=]))/ig.test(statisticsText);
                            }
                            result['diffing'] = detectDiffingStatus;
                            return result;
                        });
                        const active = defs.filter(a=>a.diffing.indicatesSomething).length>0;
                        if( active ) {
                            return Array.from(defs.filter(a=>!a.diffing.indicatesFalse));
                        } else {
                            return Array.from(defs);
                        };
                    } else {
                        /* nothing to hide, show all */
                        return Array.from(listOfControls);
                    }
                }
                function detectMode() {
                    if( !!window.reportType ) {
                        if(window.reportType=='MDD')
                            return 'mdd';
                        if(window.reportType=='diff')
                            return 'diff';
                    }
                    return 'general';
                }
                function show(d) {
                    d.controlEl.checked=true;d.controlEl.dispatchEvent(new Event('change'));
                }
                function hide(d) {
                    d.controlEl.checked=false;d.controlEl.dispatchEvent(new Event('change'));
                }
                function calcComplexity(section) {
                    return 50000; /* TODO: */
                }
                const mode = detectMode();
                const sectionListShownPreliminary = findListOfSectionsToShow(listOfControls,mode);
                let complexity = 0;
                const complexityLimit = 40000; /* TODO: bring configs to top */
                let sectionListShown = [];
                sectionListShownPreliminary.forEach(function(section) {
                    if( complexity<complexityLimit ) {
                        sectionListShown.push(section);
                        complexity+= calcComplexity(section);
                    }
                });
                /* const sectionListShown = sectionListShownPreliminary.length>16 ? [ sectionListShownPreliminary[0] ] : sectionListShownPreliminary; */
                listOfControls.forEach( function(item) {
                    isShown = sectionListShown.map(a=>a.id).includes(item.id);
                    action = isShown ? show : hide;
                    return action(item);
                } );
            }
            // 1. read data and find the list of sections in the report table
            const sectionDefs = (function(){
                const sectionDefs = [];
                const sectionElements = document.querySelectorAll('[class^="mdmreport-wrapper-section-"], [class*=" mdmreport-wrapper-section-"]');
                Array.prototype.forEach.call(sectionElements,function(sectionElement) {
                    var textTitle = `${(sectionElement.querySelector('h3') || {textContent:''}).textContent}`.replace(/^\s*?section\s+/ig,'');
                    var textCss = ( Array.from(sectionElement.classList).filter(function(name){return /^\s*?mdmreport-wrapper-section-/ig.test(name)}) || [''] )[0].replace(/^\s*?mdmreport-wrapper-section-/ig,'');
                    textTitle = textTitle.replace(/^\s*(.*?)\s*$/ig,'$1'); /* trim */
                    textCss = textCss.replace(/^\s*(.*?)\s*$/ig,'$1'); /* trim */
                    if( ( !!textTitle && (textTitle.length>0) ) || ( !!textCss && (textCss.length>0) ) ) {
                        if( !textTitle || (textTitle.length==0) ) textTitle = textCss;
                        if( !textCss || (textCss.length==0) ) textCss = textTitle;
                        textCss = textCss.replace(/[^\w\-\.]/ig,'-');
                        const statisticsEl = sectionElement.querySelector('.mdmreport-banner-table-details-statistics');
                        sectionDefs.push({
                            text: textTitle,
                            id: textCss,
                            element: sectionElement,
                            statisticsText: !!statisticsEl && (`${statisticsEl.innerText}`.trim().length>0) ? `${statisticsEl.innerText}`.trim() : null
                        });
                    }
                });
                return sectionDefs;
            })();
            // 2. add a control block
            const cssSheet = new CSSStyleSheet();
            function initSettingCss() {
                const cssSyntax = '' +
                '.mdmreport-section-wrapper { display: none; } ' +
                sectionDefs.map(function(item) {
                    const itemClassName = item['id'].replace(/[^\w\-\.]/,'');
                    return ' body .mdmreport-wrapper-section-xxx { display: block; } .mdmreport-hidesection-xxx .mdmreport-wrapper-section-xxx { display: none; } '.replaceAll('xxx',itemClassName);
                }).join('');
                cssSheet.replaceSync(cssSyntax);
                document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
            }
            function resetSettingCss() {
                cssSheet.replaceSync('');
            }
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_toc_placeholder') || document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block to show/hide sections: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                const bannerEl = document.createElement('div');
                bannerEl.classList.add('mdmreport-showhidesections-plugin');
                bannerEl.classList.add('mdmreport-banner');
                bannerEl.classList.add('mdmreport-banner-sections');
                bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><h3>Table of contents</h3><legend style="display: none;">Show/hide sections:</legend></div></fieldset></form>';
                Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',wrapErrors(function(event) {event.preventDefault();event.stopPropagation();return false;}));});
                pluginHolderEl.append(bannerEl);
                const controlsDefs = [];
                sectionDefs.forEach(function(sectionDef) {
                    try {
                        const colText = sectionDef['text'];
                        const colClassName = sectionDef['id'];
                        const sectionEl = sectionDef.element;
                        const wrapperEl = document.createElement('div');
                        wrapperEl.classList.add('mdmreport-controls-row');
                        wrapperEl.classList.add('toc-section-row');
                        wrapperEl.classList.add('mdmreport-showhidesections-plugin-row-section');
                        const labelEl = document.createElement('label');
                        labelEl.textContent = ' '; /* colText; */
                        labelEl.classList.add('mdmreport-controls');
                        labelEl.classList.add('mdmreport-controls-checkboxfulltext');
                        const checkboxEl = document.createElement('input');
                        checkboxEl.setAttribute('type','checkbox');
                        checkboxEl.setAttribute('checked','true');
                        checkboxEl.checked = true;
                        checkboxEl.addEventListener('change',wrapErrors(function(event) {
                            const checkboxEl = event.target;
                            const className = `mdmreport-hidesection-${colClassName}`;
                            const isShown = !!checkboxEl.checked;
                            if( isShown ) {
                                Array.prototype.forEach.call(document.querySelectorAll('.mdmreportpage'),function(pageEl) {
                                    pageEl.classList.remove(className);
                                    wrapperEl.classList.remove('toc-section-inactive');
                                    wrapperEl.classList.add('toc-section-active');
                                });
                            } else {
                                Array.prototype.forEach.call(document.querySelectorAll('.mdmreportpage'),function(pageEl) {
                                    pageEl.classList.add(className);
                                    wrapperEl.classList.add('toc-section-inactive');
                                    wrapperEl.classList.remove('toc-section-active');
                                });
                            };
                            if( isShown ) {
                                const possibleLinkToUnhide = sectionEl.querySelector('.mdmreport-memorysaving-hidetab-link');
                                if( possibleLinkToUnhide ) {
                                    possibleLinkToUnhide.dispatchEvent( new Event('click') );
                                    Promise.resolve().then( function() { window.dispatchEvent(new Event('mdmtable')); } );
                                }
                            }
                        }));
                        labelEl.prepend(checkboxEl);
                        const sectionTitleEl = document.createElement('span');
                        sectionTitleEl.classList.add('toc-title');
                        const sectionLinkPlaintextEl = document.createElement('span');
                        sectionLinkPlaintextEl.textContent = colText;
                        sectionLinkPlaintextEl.classList.add('toc-section-plainlink');
                        const sectionLinkHyperlinkEl = document.createElement('a');
                        sectionLinkHyperlinkEl.textContent = colText;
                        sectionLinkHyperlinkEl.classList.add('toc-section-hyperlink');
                        sectionLinkHyperlinkEl.setAttribute('href',`#${sectionDef['id']}`);
                        sectionLinkHyperlinkEl.addEventListener('click',wrapErrors(function( event ) {
                            event.preventDefault();
                            const element = sectionDef.element;
                            if(!!element.scrollIntoView) {
                                element.scrollIntoView();
                            } else {
                                const offset = element.offsetTop;
                                const navigation = 0; /* document.querySelector('.over').clientHeight */
                                const scroll = offset - navigation;
                                window.scrollTo({top:scroll,left:0,behavior:'smooth'});
                            }
                            return false;
                        }));
                        sectionTitleEl.append(sectionLinkPlaintextEl);
                        sectionTitleEl.append(sectionLinkHyperlinkEl);
                        statisticsEl = document.createElement('span');
                        statisticsEl.classList.add('toc-statistics');
                        if( !!sectionDef['statisticsText'] )
                            statisticsEl.innerText = '( ' + sectionDef['statisticsText'].replace(/(?:\r\n|\r|\n)/ig,' ') + ' )';
                        if( /\b(something\s\s*\bchanged\s*?:\s*?true)\b/i.test(statisticsEl.innerHTML) ) {
                            statisticsEl.innerHTML = statisticsEl.innerHTML.replace(/\b(something\s\s*\bchanged\s*?:\s*?true)\b/i,'<span class="mdmdiff-inlineoverlay-added">$1</span>')
                            wrapperEl.classList.add('toc-section-highlighted');
                        }
                        wrapperEl.append(labelEl);
                        wrapperEl.append(sectionTitleEl);
                        if( !!sectionDef['statisticsText'] )
                            wrapperEl.append(statisticsEl);
                        bannerEl.querySelector('fieldset').append(wrapperEl);
                        controlsDefs.push({id:sectionDef['id'],text:colText,controlEl:checkboxEl,sectionDefRef:sectionDef});
                    } catch(e) {
                        printErrors(e);
                        throw e;
                    }
                });
                (new Promise(function(resolve,reject){setTimeout(function(){return resolve(controlsDefs);},50);})).then(applyDefaultSetup).catch(function(e){
                    try {
                        resetSettingCss();
                    } catch(e) { }
                    printErrors(e);
                    throw e;
                });
                /* setTimeout(function(){ try { applyDefaultSetup(controlsDefs); } catch(e) { try { function escapeHtml(s) { const dummy = document.createElement('div'); dummy.innerText = s.replace(/\n/ig,'\\n'); return dummy.innerHTML; } printErrors(e)+'<br />'; } catch(ee) {}; try { document.removeEventListener('DOMContentLoaded',addControlBlock_ShowHideSections); } catch(ee) {} throw e; } },50); */
            }
            initSettingCss();
            initAddingControlBlock();
        } catch(e) {
            try {
                resetSettingCss();
            } catch(e) { }
            printErrors(e);
            throw e;
        }
    }
    window.addEventListener('mdmdocument',wrapErrors(addControlBlock_ShowHideSections));
