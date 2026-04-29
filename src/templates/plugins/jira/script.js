


// new cell markup: <td class="mdmreport-contentcell mdmreport-col-flagdiff" data-columnid="flagdiff">Diff flag</td>
// new cell markup: <td class="mdmreport-contentcell mdmreport-col-label">Serial number</td>
// old cell markup: <td class="mdmreport-contentcell">October</td>


   /* === jira connection js === */

    const validDomains = ['lrwjira.atlassian.net','www.lrwjira.atlassian.net','www.materialplus.atlassian.net','materialplus.atlassian.net'];
    
    
    let bannerHolderPromiseResolve = () => { throw new Error('please jiraPlugin_init the promise first'); };
    let bannerHolderPromiseReject = () => { throw new Error('please jiraPlugin_init the promise first'); };
    const bannerHolderPromise = new Promise((resolve,reject)=>{ bannerHolderPromiseResolve = resolve; bannerHolderPromiseReject = reject; });
    let runPromiseResolve = () => { throw new Error('please jiraPlugin_init the promise first'); };
    let runPromiseReject = () => { throw new Error('please jiraPlugin_init the promise first'); };
    const runPromise = new Promise((resolve,reject)=>{ runPromiseResolve = resolve; runPromiseReject = reject; });
    function sanitizeCellText(s) {
        return s.replace(/&\#(\d+);/i,function(n,n1){if(isFinite(+n1)) return String.fromCharCode(+n1);else return n;});
    }
    function parsePropertiesText(s) {
        const results = [];
        if( /^\s*?$/.test(s) )
            return results;
        const matches = s.match( /^\s*?,?\s*?(\w+)\s*?=\s*?"((?:(?:[^"])|(?:""))*?)"((?:\s*?,\s*?\w+\s*?=\s*?"(?:(?:[^"])|(?:""))*?")*?)\s*?$/ );
        if( !!matches ) {
            results.push({name:matches[1],value:matches[2].replace(/""/ig,'"')});
            if( !!matches[3] ) {
                results.push(...parsePropertiesText(matches[3]));
            }
            return results;
        } else {
            // // TODO: why throw an exception and stop? Can we just ignore?
            // // throw new Error(`can't parse properties at [${s}]`);
            // printErrors(`Warning: Jira connection plugin: Reading custom properties: can't parse this as properties: "${s}"`);
            // return results;
            // // Actually, no, the function should read the properties, if it can't, it fails; if we want to handle failure differently, i.e. not break - we can do at a level where we check results of this fn
            throw new Error(`Reading custom properties: can't parse this as properties: "${s}"`);
        }
    }
    function itemNameLookup(itemName,propertiesData,sectionName) {
        function normalizeSectionId(id) {
            return id.replace(/_/ig,' ').replace(/\s/ig,' ').replace(/\bx\d+\b/ig,' ').replace(/\s+/ig,' ').replace(/^\s*/ig,'').replace(/\s*$/ig,'');
        }
        try {
            if(false) { /* ( /^\s*?Info\s*?\:/.test(itemName) ) { */
                // info item - skip
                return null;
            /* } else if(normalizeSectionId(sectionName)=='') { */
                /* show we search for jira for '' (root) item? I think yes, I will not skip */
                /* return null; */
            } else if( (/\bshared\b\s*?\blist(?:s)?\b/ig.test(normalizeSectionId(sectionName))) && (/^\s*?\w+/.test(itemName)) ) {
                /* ah it's now "shared_x95_lists" */
                // is a shared list
                return itemName.replace(/^\s*?(\w+)\b.*?$/ig,'$1').replace(/^\s*?SL_/ig,'');
            } else if( (normalizeSectionId(sectionName)=='fields') ) {
                // "fields" (normal questions) - let's look up the FullName property
                const properties = propertiesData[itemName];
                const propertyListLcase = properties.map(a=>a.name.toLowerCase());
                if( /^\s*?QCData\.Flags\b/.test(itemName) ) {
                    // A QC Flag - let's look up the "AppliesTo" property
                    if( propertyListLcase.includes('AppliesTo'.toLowerCase()) ) {
                        // TODO: best match. or all matches?
                        const appliesto = properties[propertyListLcase.indexOf('AppliesTo'.toLowerCase())].value.replace(/^\s*?Question\s*?\-\s*/ig,'').replace(/^\s*/,'').replace(/\s*$/,'');
                        return appliesto;
                    }
                }
                if( propertyListLcase.includes('FullName'.toLowerCase()) ) {
                    const fullname = properties[propertyListLcase.indexOf('FullName'.toLowerCase())].value.replace(/^\s*/,'').replace(/\s*$/,'');
                    return fullname;
                }
                if( /\.(?:categories|elements)\s*?\[\s*?.*?\s*?\]\s*?$/ig.test(itemName) ) {
                    const refItemName = itemName.replace(/\.(?:categories|elements)\s*?\[\s*?.*?\s*?\]\s*?$/ig,'');
                    const refItemProperties = propertiesData[refItemName];
                    const refItemPropertyListLcase = refItemProperties.map(a=>a.name.toLowerCase());
                    if( refItemPropertyListLcase.includes('FullName'.toLowerCase()) ) {
                        const fullname = refItemProperties[refItemPropertyListLcase.indexOf('FullName'.toLowerCase())].value.replace(/^\s*/,'').replace(/\s*$/,'');
                        return fullname;
                    }
                }
                return null
            } else if( (normalizeSectionId(sectionName)=='pages') ) {
                // "pages" - usually tickets are not issued for pages, skip
                return null
            } else
                return null;
        } catch(e) {
            printErrors(e);
            throw e;
        }
    }
    function getJobNumberProperty(rowsEl,rowBannerEl) {
        try {
            const promise = new Promise(function(resolve,reject) {
                try {
                    const rowsWithHdataEl = rowsEl; // rowsEl.filter(function(tr){ const cols = Array.from(tr.querySelectorAll('td')); if(cols.length>1) { return /^(?:\s*?(?:(?:mdd|mdm|hdata)\.)?Properties\s*?)|(?:\s*.*?\bMDM\b.*?\s*)$/ig.test(sanitizeCellText(cols[1].textContent)); } else return false; });
                    Array.from(rowsEl).forEach(function(row){
                        function detectNameColumnsIndex(rowsEl) {
                            const resultColIndices = [];
                            if(rowsEl.length>0) {
                                const rowEl = rowsEl[0];
                                const colsEl = rowEl.querySelectorAll('td');
                                Array.from(colsEl).forEach(function(colEl,i){
                                    colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                                    colIdsMatching = colIds.filter(a=>/^\s*?name\b.*?/ig.test(a.replace(/_/ig,' ')));
                                    if(colIdsMatching.length>0)
                                        resultColIndices.push(i);
                                });
                            }
                            if( resultColIndices.length>0 ) {
                                return resultColIndices[0];
                            } else {
                                return -1;
                            }
                        }
                        function detectDiffColumnsIndices(rowsEl) {
                            const resultColIndices = [];
                            if(rowsEl.length>0) {
                                const rowEl = rowsEl[0];
                                const colsEl = rowEl.querySelectorAll('td');
                                Array.from(colsEl).forEach(function(colEl,i){
                                    colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                                    colIdsMatching = colIds.filter(a=>/^\s*?flagdiff\b.*?/ig.test(a.replace(/_/ig,' ')));
                                    if(colIdsMatching.length>0)
                                        resultColIndices.push(i);
                                });
                            }
                            if( resultColIndices.length>0 ) {
                                return resultColIndices[0];
                            } else {
                                return -1;
                            }
                        }
                        function detectPropertiesColumnsIndices(rowsEl) {
                            const resultColIndices = [];
                            if(rowsEl.length>0) {
                                const rowEl = rowsEl[0];
                                const colsEl = rowEl.querySelectorAll('td');
                                Array.from(colsEl).forEach(function(colEl,i){
                                    colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                                    colIdsMatching = colIds.filter(a=>/^\s*?properties.*?/ig.test(a));
                                    if(colIdsMatching.length>0)
                                        resultColIndices.push(i);
                                });
                                //const isAPropertiesColumn = s => /^(?:(?:&#32;)|(?:\s))*?(?:Custom)\s*?properties(?:(?:&#32;)|(?:\s))*?(?:(?:&#40;)|(?:\())*?.*?(?:(?:&#42;)|(?:\)))*?(?:(?:&#32;)|(?:\s))*?$/ig.test(s);
                                //const cols = Array.from(colsEl).map(cellEl=>sanitizeCellText(cellEl.innerText||cellEl.textContent).replace(/^\s*?\(\s*?(?:Left|Right)\s*?MDD\s*?\)\s*/ig,''));
                                //const colsWithProperties = cols.map((colText,colIndex)=>{if(colIndex<2)return false;if(isAPropertiesColumn(colText))return colIndex;else return false;});
                                //colsWithProperties.forEach(e=>{if(!!e)propertiesColIndices.push(e);});
                            }
                            return resultColIndices;
                        }
                        const propertiesColIndices = detectPropertiesColumnsIndices(rowsEl);
                        const colsEl = Array.from(row.querySelectorAll('td'));
                        const propertiesData = {};
                        const itemNameColIndex = detectNameColumnsIndex(rowsEl);
                        const cols = Array.from(colsEl).map(cellEl=>sanitizeCellText(cellEl.innerText||cellEl.textContent).replace(/^\s*?\(\s*?(?:Left|Right)\s*?MDD\s*?\)\s*/ig,''));
                        const itemName = itemNameColIndex>=0 ? cols[itemNameColIndex] : '';
                        const properties = [];
                        const parsePropertiesTextFailSafe = function(s){
                            try {
                                return parsePropertiesText(s);
                            } catch(e) {
                                err_msg = `${e} (processing row: "${itemName})"`.replace('Error','Warning');
                                printErrors(err_msg);
                                return [];
                            }
                        }
                        propertiesColIndices.forEach(colIndex=>{
                            properties.push(...parsePropertiesTextFailSafe(cols[colIndex]));
                        });
                        //if( !!propertiesData[itemName] ) throw new Error(`grabbing properties: duplicate row at #${i}:  ${itemName}`);
                        //propertiesData[itemName] = properties.reverse(); // we reverse the order so that if we find the first matching property with indexOf it comes from the last column that stands for the right, the newer mdd
                        const propertyCellContent = properties.reduce(function(acc,e){return ({...acc,[e.name]:e.value});},{});
                        if( Object.keys(propertyCellContent).includes('JobNumber') ) {
                            return resolve(propertyCellContent['JobNumber']);
                        }
                    });
                } catch(e) {
                    printErrors(e);
                    throw e;
                }
                return reject('JobJumber not found');
            });
            return promise;
        } catch(e) {
            printErrors(e);
            throw e;
        }
    }
    function jiraPlugin_init(){
        try {
            /* jira - related tickets lookup */
            /* https://materialplus.atlassian.net/jira/software/c/projects/P123456/issues/?jql=project%20%3D%20%22P123456%22%20AND%20%28resolution%3Dunresolved%29%20AND%20%28not%20%28status%20in%20%28Resolved%2CDone%2CClosed%29%29%29%20AND%20%28not%20%28status%20in%20%28%22Ready%20for%20Stage%22%2C%22Need%20more%20Information%22%29%29%29%20ORDER%20BY%20key%20ASC */
            /* import urllib.parse */
            /* print('https://materialplus.atlassian.net/jira/software/c/projects/P123456/issues/?jql='+(urllib.parse.quote(urllib.parse.unquote('project%20%3D%20%22P123456%22%20AND%20%28resolution%3Dunresolved%29%20AND%20%28not%20%28status%20in%20%28Resolved%2CDone%2CClosed%29%29%29%20AND%20%28not%20%28status%20in%20%28%22Ready%20for%20Stage%22%2C%22Need%20more%20Information%22%29%29%29%20ORDER%20BY%20key%20ASC'), safe=''))) */

            const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
            if(!pluginHolderEl) throw new Error('adding block to show/hide columns: failed to find proper place for the element: #mdmreport_plugin_placeholder');
            const tablesEl = document.querySelectorAll('table.mdmreport-table');
            const bannerEl = document.createElement('div');
            bannerEl.className = 'mdmreport-layout-plugin mdmreport-banner mdmreport-banner-jiratixlink';
            bannerEl.innerHTML = '<legend>Jira - related tickets lookup</legend>';
            const divBannerHolderEl = document.createElement('div');
            const clickmeRevealBannerEl = document.createElement('a');
            clickmeRevealBannerEl.setAttribute('href','#!');
            clickmeRevealBannerEl.setAttribute('onclick','javascript: return false;');
            clickmeRevealBannerEl.textContent = "   (show)"
            clickmeRevealBannerEl.addEventListener('click',function(event){event.preventDefault();event.stopPropagation();bannerHolderPromiseResolve({bannerHolderEl:divBannerHolderEl,tablesEl});clickmeRevealBannerEl.remove();return false;});
            bannerEl.querySelector('legend').append(clickmeRevealBannerEl);
            bannerEl.append(divBannerHolderEl);
            pluginHolderEl.append(bannerEl);
            try {
                window.removeEventListener('mdmdocument',jiraPlugin_init);
            } catch(ee) {}
        } catch(e) {
            printErrors(e);
            try {
                window.removeEventListener('mdmdocument',jiraPlugin_init);
            } catch(ee) {}
            throw e;
        }
    }
    function jiraPlugin_workaddelementstotables(  { getJiraUrl, tablesEl, jiraPlugin_clearUp } ) {
        try {
            Array.from(tablesEl).forEach(function(tableEl) {
                const sectionName = (function(tableEl){
                    // find closest section elemt and its class
                    var resultingId = '';
                    const closestSecEl = tableEl.closest('[class^="mdmreport-wrapper-section-"], [class*=" mdmreport-wrapper-section-"]');
                    if(closestSecEl) {
                        Array.from(closestSecEl.classList).forEach(function(className){
                            if(  /^\s*?mdmreport-wrapper-section-(.*?)\s*?$/.test(className) ) {
                                resultingId = className.replace(/^\s*?mdmreport-wrapper-section-(.*?)\s*?$/,'$1');
                            }
                        });
                    }
                    return resultingId;
                })(tableEl);
                const rowsEl = tableEl.querySelectorAll('tr');
                jiraPlugin_clearUp();
                function detectNameColumnsIndex(rowsEl) {
                    const resultColIndices = [];
                    if(rowsEl.length>0) {
                        const rowEl = rowsEl[0];
                        const colsEl = rowEl.querySelectorAll('td');
                        Array.from(colsEl).forEach(function(colEl,i){
                            colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                            colIdsMatching = colIds.filter(a=>/^\s*?name\b.*?/ig.test(a.replace(/_/ig,' ')));
                            if(colIdsMatching.length>0)
                                resultColIndices.push(i);
                        });
                    }
                    if( resultColIndices.length>0 ) {
                        return resultColIndices[0];
                    } else {
                        return -1;
                    }
                }
                function detectDiffColumnsIndices(rowsEl) {
                    const resultColIndices = [];
                    if(rowsEl.length>0) {
                        const rowEl = rowsEl[0];
                        const colsEl = rowEl.querySelectorAll('td');
                        Array.from(colsEl).forEach(function(colEl,i){
                            colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                            colIdsMatching = colIds.filter(a=>/^\s*?flagdiff\b.*?/ig.test(a.replace(/_/ig,' ')));
                            if(colIdsMatching.length>0)
                                resultColIndices.push(i);
                        });
                    }
                    if( resultColIndices.length>0 ) {
                        return resultColIndices[0];
                    } else {
                        return -1;
                    }
                }
                function detectPropertiesColumnsIndices(rowsEl) {
                    const resultColIndices = [];
                    if(rowsEl.length>0) {
                        const rowEl = rowsEl[0];
                        const colsEl = rowEl.querySelectorAll('td');
                        Array.from(colsEl).forEach(function(colEl,i){
                            colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                            colIdsMatching = colIds.filter(a=>/^\s*?properties.*?/ig.test(a));
                            if(colIdsMatching.length>0)
                                resultColIndices.push(i);
                        });
                        //const isAPropertiesColumn = s => /^(?:(?:&#32;)|(?:\s))*?(?:Custom)\s*?properties(?:(?:&#32;)|(?:\s))*?(?:(?:&#40;)|(?:\())*?.*?(?:(?:&#42;)|(?:\)))*?(?:(?:&#32;)|(?:\s))*?$/ig.test(s);
                        //const cols = Array.from(colsEl).map(cellEl=>sanitizeCellText(cellEl.innerText||cellEl.textContent).replace(/^\s*?\(\s*?(?:Left|Right)\s*?MDD\s*?\)\s*/ig,''));
                        //const colsWithProperties = cols.map((colText,colIndex)=>{if(colIndex<2)return false;if(isAPropertiesColumn(colText))return colIndex;else return false;});
                        //colsWithProperties.forEach(e=>{if(!!e)propertiesColIndices.push(e);});
                    }
                    return resultColIndices;
                }
                const propertiesData = {};
                const itemNameColIndex = detectNameColumnsIndex(rowsEl);
                const diffFlagColIndex = detectDiffColumnsIndices(rowsEl);
                const propertiesColIndices = detectPropertiesColumnsIndices(rowsEl);
                const isTemporarilyMovedRow = s => /^\s*?\(\s*?moved\s*?\)\s*?$/ig.test(s);
                Array.prototype.forEach.call(rowsEl,function(rowEl,i) {
                    const colsEl = rowEl.querySelectorAll('td');
                    const cols = Array.from(colsEl).map(cellEl=>sanitizeCellText(cellEl.innerText||cellEl.textContent).replace(/^\s*?\(\s*?(?:Left|Right)\s*?MDD\s*?\)\s*/ig,''));
                    if( i==0 ) {
                        /* not adding jira link in zero (banner) row */
                    } else {
                        const itemName = itemNameColIndex>=0 ? cols[itemNameColIndex] : '';
                        const diffFlag = diffFlagColIndex>=0 ? cols[diffFlagColIndex] : '';
                        if( isTemporarilyMovedRow(diffFlag) )
                            return;
                        const properties = [];
                        const parsePropertiesTextFailSafe = function(s){
                            try {
                                return parsePropertiesText(s);
                            } catch(e) {
                                err_msg = `${e} (processing row: "${itemName})"`.replace('Error','Warning');
                                printErrors(err_msg);
                                return [];
                            }
                        }
                        propertiesColIndices.forEach(colIndex=>{
                            properties.push(...parsePropertiesTextFailSafe(cols[colIndex]));
                        });
                        //if( !!propertiesData[itemName] ) throw new Error(`grabbing properties for jira connections: duplicate row at #${i}:  ${itemName}`);
                        if( !propertiesData[itemName] ) propertiesData[itemName] = [];
                        propertiesData[itemName] = [ ...propertiesData[itemName], ...properties.reverse() ]; // we reverse the order so that if we find the first matching property with indexOf it comes from the last column that stands for the right, the newer mdd
                    }
                });
                Array.prototype.forEach.call(rowsEl,function(rowEl,i) {
                    const colsEl = Array.from(rowEl.querySelectorAll('td'));
                    const colAddIndex = colsEl.length;
                    const colAddEl = document.createElement('td');
                    colAddEl.classList.add('mdmreport-contentcell');
                    colAddEl.classList.add('mdmreport-col--jiraplugin');
                    colAddEl.classList.add('mdmrep-diff-jiraaddon-col');
                    colAddEl.classList.add(`mdmreport-colindex-${colAddIndex}`);
                    if(i===0) {
                        /* header row */
                        colAddEl.textContent = "Jira - possible ticket lookup link"
                    } else {
                        function detectNameColumnsIndex(rowsEl) {
                            const resultColIndices = [];
                            if(rowsEl.length>0) {
                                const rowEl = rowsEl[0];
                                const colsEl = rowEl.querySelectorAll('td');
                                Array.from(colsEl).forEach(function(colEl,i){
                                    colIds = Array.from(colEl.classList).filter(a=>/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig.test(a)).map(a=>a.replace(/^\s*?mdmreport-col-(\w[^\s]*?)\s*?$/ig,'$1'));
                                    colIdsMatching = colIds.filter(a=>/^\s*?name\b.*?/ig.test(a.replace(/_/ig,' ')));
                                    if(colIdsMatching.length>0)
                                        resultColIndices.push(i);
                                });
                            }
                            if( resultColIndices.length>0 ) {
                                return resultColIndices[0];
                            } else {
                                return -1;
                            }
                        }
                        const itemNameColIndex = detectNameColumnsIndex(rowsEl);
                        if( (itemNameColIndex>=0) ) {
                            const itemName = colsEl[itemNameColIndex].textContent;
                            const possibleItemName = itemNameLookup(sanitizeCellText(itemName),propertiesData,sectionName);
                            if( !!possibleItemName && (typeof possibleItemName==='string') && (possibleItemName.length>0) ) {
                                const linkurl = getJiraUrl(possibleItemName);
                                const linkEl = document.createElement('a');
                                linkEl.setAttribute('href',linkurl);
                                linkEl.setAttribute('_target','blank');
                                linkEl.textContent = decodeURIComponent(linkurl);
                                colAddEl.append(linkEl);
                            }
                        }
                    }
                    rowEl.append(colAddEl);
                });
            });
        } catch(e) {
            printErrors(e);
            throw e;
        }
    }
    function jiraPlugin_pluginpanelunhidden( { bannerHolderEl, tablesEl } ) {
        try {
            const bannerContentEl = document.createElement('div');
            const propertyJobNumber = '123456';
            bannerContentEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"></fieldset></form>';
            Array.prototype.forEach.call(bannerContentEl.querySelectorAll('form'),function(formEl){formEl.addEventListener('submit',function(event){event.preventDefault();event.stopPropagation();return false;});});
            bannerContentEl.querySelector('fieldset').innerHTML = '<div class="mdmreport-controls-group"><label>PROJECT_NUM:  </label><input type="text" value="P123456" /></div><div class="mdmreport-controls-group"><label>Base url:  </label><input type="text" value="https://materialplus.atlassian.net/jira/software/c/projects/P123456/issues/?jql=" /></div></div><div class="mdmreport-controls-group"><label>JQL:  </label><input type="text" value="project = &quot;P123456&quot; AND ((summary~&quot;<<QUESTIONNAME>>&quot;) OR (summary~&quot;<<QUESTIONSHORTNAME>>&quot;) OR (question~&quot;&#92;&quot;<<QUESTIONWANAME>>&#92;&quot;&quot;)) AND (resolution=unresolved) AND (not (status in (Resolved,Done,Closed))) AND (not (status in (&quot;Ready for Stage&quot;,&quot;Need more Information&quot;))) ORDER BY key ASC" /></div><div><input type="button" value="Go!" /><p style="color: #555;"><small>Hint: you can use these keywords that will be replaced with question name: &lt;&lt;QUESTIONFULLNAME&gt;&gt;, &lt;&lt;QUESTIONSHORTNAME&gt;&gt;, &lt;&lt;QUESTIONNAME&gt;&gt;, &lt;&lt;QUESTIONWANAME&gt;&gt;.</small></p></div>'.replaceAll('123456',propertyJobNumber);
            const inp1El = bannerContentEl.querySelector('fieldset').querySelectorAll('input')[0];
            const inp2El = bannerContentEl.querySelector('fieldset').querySelectorAll('input')[1];
            const inp3El = bannerContentEl.querySelector('fieldset').querySelectorAll('input')[2];
            inp1El.addEventListener('change',function(event){ event.preventDefault(); inp2El.value = inp2El.value.replace(/(\/projects\/)([\w\-]+)(\/)/,`$1${inp1El.value}$3`); inp2El.dispatchEvent(new Event('change')); inp3El.value = inp3El.value.replace(/(\bproject\b\s*?=\s*?"\s*?)([\w\-]+)(\s*?")/,`$1${inp1El.value}$3`); inp3El.dispatchEvent(new Event('change')); return false; });
            inp1El.addEventListener('keypress',function(event){  inp1El.dispatchEvent(new Event('change'));});
            inp2El.addEventListener('keypress',function(event){  inp2El.dispatchEvent(new Event('change'));});
            inp3El.addEventListener('keypress',function(event){  inp3El.dispatchEvent(new Event('change'));});
            inp1El.addEventListener('keyup',function(event){  inp1El.dispatchEvent(new Event('change'));});
            inp2El.addEventListener('keyup',function(event){  inp2El.dispatchEvent(new Event('change'));});
            inp3El.addEventListener('keyup',function(event){  inp3El.dispatchEvent(new Event('change'));});
            const promiseTmp = Promise.resolve(); // why? what's the reason? are we just trying to call it async in a separate flow, not blocking interface? probably
            promiseTmp.then(function(){
                try {
                    const rowsPotentiallyMDMPropEl = document.querySelectorAll('.mdmreport-wrapper-section-mdmproperties table.mdmreport-table tr.mdmreport-record:not(.mdmreport-record-header), .mdmreport-wrapper-section-fields table.mdmreport-table tr.mdmreport-record:not(.mdmreport-record-header)');
                    const rowsBannerEl = document.querySelectorAll('table.mdmreport-table tr.mdmreport-record.mdmreport-record-header');
                    if(!(rowsBannerEl.length>0)) throw new Error('Not found a row with column headers for checking properties to grab JobNumber value');
                    const rowBannerEl = rowsBannerEl[0];
                    const weGetJobnumberPromise = getJobNumberProperty(Array.from(rowsPotentiallyMDMPropEl),rowBannerEl);
                    weGetJobnumberPromise.then( function(val) {
                        try {
                            const propertyJobNumber = `P${`${val}`.replace(/^\s*?(P?)(\d\w+)\s*?$/,'$2')}`;
                            inp1El.value = propertyJobNumber;
                            inp1El.dispatchEvent(new Event('change'));
                        } catch(e) {
                            printErrors(e);
                            throw e;
                        }
                    });
                } catch(e) {
                    printErrors(e);
                    throw e;
                }
            });
            const submitEl = bannerContentEl.querySelector('fieldset').querySelectorAll('input[type="button"]')[0];
            submitEl.addEventListener('click',function(event){
                event.preventDefault();
                try {
                    const val2 = inp2El.value;
                    const val3 = inp3El.value;
                    const prepJiraString = function(jiraStr,itemName) { let name = itemName; let shortName = itemName; let fullName = itemName; let waName = itemName; if(/^\s*?(DT_)(\w+)$/.test(itemName)) { name = itemName.replace(/^\s*?(DT)_(\w+)$/,'$2'); shortName = name; waName = `${'DT'}. ${name}`; } else if(/^\s*?(DV)_(\w+)$/.test(itemName)) { /* all good */ } else if(/^\s*?([a-zA-Z]+[0-9]+\w*?)_(\w+)$/.test(itemName)) { name = itemName.replace(/^\s*?([a-zA-Z]+[0-9]+\w*?)_(\w+)$/,'$2'); shortName = itemName.replace(/^\s*?([a-zA-Z]+[0-9]+\w*?)_(\w+)$/,'$1'); waName = `${shortName}. ${name}`; }; return jiraStr.replaceAll('<<QUESTIONFULLNAME>>',fullName).replaceAll('<<QUESTIONSHORTNAME>>',shortName).replaceAll('<<QUESTIONWANAME>>',waName).replaceAll('<<QUESTIONNAME>>',name); };
                    const getJiraUrl = function(itemName) { return `${decodeURIComponent(val2)}${encodeURIComponent(prepJiraString(val3,itemName))}`; };
                    if( !validDomains.map(a=>a.toLowerCase()).includes((new URL(getJiraUrl(''))).hostname.toLowerCase()) )
                        throw new Error(`Not valid jira domain! It has to be in this list: [ ${validDomains.join(', ')} ], or, update the code, it's easy; search for "validDomains"`);
                    runPromiseResolve(  { getJiraUrl, tablesEl, jiraPlugin_clearUp } );
                } catch(e) {
                    printErrors(e);
                    throw e;
                }
                return false;
            });
            function jiraPlugin_clearUp() {
                /* bannerContentEl.remove(); */
                bannerContentEl.innerText = 'Done, see the right most column in the table';
            };
            bannerHolderEl.append(bannerContentEl);
        } catch(e) {
            printErrors(e);
            try {
                window.removeEventListener('mdmdocument',jiraPlugin_init); // trying to save memory and clear this function from memory but that's stupid - as we have a reference here, it is stil in memory; it should be cleared at a different, outer level
            } catch(ee) {}
            throw e;
        }
    }
    runPromise.then(function(params){
        const process = function(){
            const tablesEl = Array.from(document.querySelectorAll('table.mdmreport-table')).filter(tableEl=>!tableEl.querySelector('.mdmrep-diff-jiraaddon-col'));
            return jiraPlugin_workaddelementstotables({...params,tablesEl});
        }
        window.addEventListener('mdmtable',wrapErrors(process));
        return process();
    });
    runPromise.then(function(){window.dispatchEvent(new Event('resize'));});
    bannerHolderPromise.then(jiraPlugin_pluginpanelunhidden);
    window.addEventListener('mdmdocument',wrapErrors(jiraPlugin_init));
