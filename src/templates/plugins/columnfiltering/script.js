
    /* === column filtering js === */

    function addElementsToTables_TableFilters() {
        function bubbleException(e) {
            printErrors(e);
            throw e;
        }
        try {
            // 1. read data and find the list of sections in the report table
            const sectionElements = document.querySelectorAll('[class^="mdmreport-wrapper-section-"], [class*=" mdmreport-wrapper-section-"]');
            Array.prototype.forEach.call(sectionElements,function(sectionElement) {
                if( sectionElement.querySelector('.mdmreport-tablefilterplugin-controls') )
                    return;
                var textTitle = `${(sectionElement.querySelector('h3') || {textContent:''}).textContent}`.replace(/^\s*?section\s+/ig,'');
                const sectionClasses = Array.from(sectionElement.classList).filter(function(name){return /^\s*?mdmreport-wrapper-section-/ig.test(name)});
                const sectionClassesUnique = sectionClasses.filter(function(className){return document.querySelectorAll('.'+className).length==1});
                if( !(sectionClassesUnique.length>0) ) return;
                const sectionClass = sectionClassesUnique[0];
                var textCss = sectionClass.replace(/^\s*?mdmreport-wrapper-section-/ig,'');
                textTitle = textTitle.replace(/^\s*(.*?)\s*$/ig,'$1'); // trim
                textCss = textCss.replace(/^\s*(.*?)\s*$/ig,'$1'); // trim
                if( !( ( !!textTitle && (textTitle.length>0) ) || ( !!textCss && (textCss.length>0) ) ) ) return;
                if( !textTitle || (textTitle.length==0) ) textTitle = textCss;
                if( !textCss || (textCss.length==0) ) textCss = textTitle;
                textCss = textCss.replace(/[^\w\-\.]/ig,'-');
                const sectionDef = {
                    text:textTitle,
                    id:textCss,
                    tableElement:sectionElement.querySelector('table.mdmreport-table'),
                    sectionClass: sectionClass
                    };
                if(!sectionDef.tableElement) return;
                const headerRowEls = sectionDef.tableElement.querySelectorAll('tr.mdmreport-record-header');
                const allRows = Array.from(sectionDef.tableElement.querySelectorAll('tr.mdmreport-record:not(.mdmreport-record-header)')).map(function(element,index) {
                    const texts = Array.from(element.querySelectorAll('td.mdmreport-contentcell')).map(function(el){
                        var result = el.innerText||el.textContent;
                        if( el.hasAttribute('data-added') )
                            result = result + ' ' + el.getAttribute('data-added');
                        Array.from(el.querySelectorAll('[data-added]')).forEach(function(el){
                            result = result + ' ' + el.getAttribute('data-added');
                        });
                        return result;
                    });
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
                            function doesCellMatchFilter(cellContents,checkStr){
                                return cellContents.toLowerCase().includes(checkStr.toLowerCase());
                            }
                            const cellContents = rowDef.texts[colIndex];
                            const isMatching = (checkStr.length==0) || doesCellMatchFilter(cellContents,checkStr);
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
                    controlEl.addEventListener('change',wrapErrors(handleChange));
                    controlEl.addEventListener('keyup',wrapErrors(handleChange));
                    controlEl.addEventListener('keydown',wrapErrors(handleChange));
                    controlEl.addEventListener('keypress',wrapErrors(handleChange));
                    cellEl.append(controlGroupElAdd);
                    cellEl.classList.add('mdmreport-tablefilterplugin-enchancedcell');
                });
            });
        } catch(e) {
            printErrors(e);
            throw e;
        }
    }
    function addControlBlock_TableFilters() {
        try {
            // 2. add a control block
            function initAddingControlBlock() {
                const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
                if(!pluginHolderEl) throw new Error('adding block with table filters: failed to find proper place for the element: #mdmreport_plugin_placeholder');
                const bannerEl = document.createElement('div');
                bannerEl.className = 'mdmreport-tablefilters-plugin mdmreport-banner mdmreport-banner-tablefilters';
                bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Add the ability to filter tables by content</legend></div><input type="submit" value="Yes, add this please!" /></fieldset></form>';
                Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',wrapErrors(function(event) {
                    try {
                        event.preventDefault();
                        event.stopPropagation();
                        addElementsToTables_TableFilters();
                        //bannerEl.classList.add('mdmreport-format-hidden');
                        bannerEl.innerHTML = '<p>Add the ability to filter tables by content</p><span>Done, input boxes are added below the header line in every table.</span>';
                        return false;
                    } catch(e) {
                        printErrors(e);
                        throw e;
                    }
                }));});
                // pluginHolderEl.append(bannerEl); // we don't want the user to press "add", we are just adding it, it's so nice to have, it is now added automatically
                setTimeout(addElementsToTables_TableFilters,400);
                window.addEventListener('mdmreport_table',wrapErrors(addElementsToTables_TableFilters));
            }
            initAddingControlBlock();
            document.removeEventListener('DOMContentLoaded',addControlBlock_TableFilters);
        } catch(e) {
            printErrors(e);
            throw e;
        }
    }
    window.addEventListener('DOMContentLoaded',wrapErrors(addControlBlock_TableFilters));
