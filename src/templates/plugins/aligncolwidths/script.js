    /* === align col widths js === */
function alignColWidthsInit() {
    /* const tables_all = document.querySelectorAll('.mdmreport-table'); */
    const cssSheet = new CSSStyleSheet();
    document.adoptedStyleSheets = [...document.adoptedStyleSheets,cssSheet];
    function process() {
        try {
            const widthDefault = 300;
            const tables_all = document.querySelectorAll('.mdmreport-table');
            // first, clear out previous formatting
            Array.prototype.forEach.call(tables_all,function(tableEl) {
                tableEl.classList.remove('mdmreport-table-formatting-fixeddimensions');
            });
            cssSheet.replaceSync('');
            (function() {
                const widthRaw = widthDefault;
                const widthVal = `${widthRaw}px`;
                const cssSyntax = `.mdmreport-table td { max-width: ${widthVal}; }`
                cssSheet.replaceSync(cssSyntax);
            })();
            /* stop if data is too big */
            if( Array.from(document.querySelectorAll('.mdmreport-table td')).length>500*16*26 )
                return;
            // now find new width values
            const colWidthsData = (function(){
                const result = [];
                Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                    const rowElements = tableEl.querySelectorAll('tr.mdmreport-record');
                    if( rowElements.length>0 ) {
                        colElements = rowElements[0].querySelectorAll('tr.mdmreport-record>td');
                        Array.prototype.forEach.call(colElements,function(colEl,colIndex) {
                            if(!result[colIndex]) result[colIndex] = [];
                            result[colIndex][tableIndex] = colEl.getBoundingClientRect().width;
                        });
                    }
                });
                return result;
            })();
            const colMaxIndex = colWidthsData.length-1;
            const colParentWidth = (function(){
                var result = 0;
                Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                    if(!(result>0)) {
                        if(!!tableEl.parentElement) {
                            result = tableEl.parentElement.getBoundingClientRect().width;
                        }
                    }
                });
                return result;
            })();
            const numColsCounted = (function(){
                const isValValid = val => isFinite(val) && (val>0);
                var result = [];
                for(let colIndex=0;colIndex<=colMaxIndex;++colIndex) {
                    Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                        const val = colWidthsData[colIndex][tableIndex];
                        if(isValValid(val)) {
                            result[colIndex] = 1;
                        }
                    });
                }
                return result.reduce((acc,e)=>acc+(e>0?1:0),0);
            })();
            const colMinWidth = 60;
            const colMaxAllowedWidth = (function(){
                var result = document.querySelector('body').getBoundingClientRect().width;
                if( numColsCounted==1 ) {
                    result = colParentWidth;
                } else {
                    const resultVerA = colParentWidth - colMinWidth * 1.19 >= colMinWidth ? colParentWidth - colMinWidth * 1.19 : colMinWidth;
                    const resultVerB = (colParentWidth>(numColsCounted+.24)*colMinWidth?colParentWidth:(numColsCounted+.24)*colMinWidth) / numColsCounted;
                    result = (resultVerA * resultVerB) ** .5;
                }
                return result;
            })();
            const colWidthsAverageAcrossSections = (function(){
                const isValValid = val => isFinite(val) && (val>0);
                var result = [];
                for(let colIndex=0;colIndex<=colMaxIndex;++colIndex) {
                    var numSectionsCounted = 0;
                    if(!result[colIndex]) result[colIndex] = 0;
                    Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                        const val = colWidthsData[colIndex][tableIndex];
                        if(isValValid(val)) {
                            if(!result[colIndex]) result[colIndex] = 0;
                            result[colIndex] += val;
                            numSectionsCounted++;
                        }
                    });
                    result[colIndex] = numSectionsCounted>0 ? result[colIndex] / numSectionsCounted : 0;
                }
                return result;
            })();
            const colWidthsAdjusted = (function(){
                const isValValid = val => isFinite(val) && (val>0);
                var result = Array.from(colWidthsAverageAcrossSections);
                const sum = result.reduce((acc,val)=>isValValid(val)?(acc+val):acc,0);
                if( sum<colParentWidth ) {
                    /* const multiplier = (colParentWidth-0.00001) / sum; */
                    /* result = result.map(a=>a*multiplier); */
                    const isBig = a => a>widthDefault*.99;
                    const addPart = result.map(a=>({width:a,addCount:a>0?(isBig(a)?4:1):0}));
                    const multiplier = ( colParentWidth-0.00001 + addPart.reduce((acc,e)=>acc+colMinWidth*e.addCount,0) ) / addPart.reduce((acc,e)=>acc+e.width+colMinWidth*e.addCount,0);
                    if(!(multiplier>=1)) throw new Error('resizing columns: wrong multiplier');
                    result = addPart.map(a=>a.width*multiplier+colMinWidth*a.addCount*(multiplier-1));
                }
                result = result.map( a => a>=colMinWidth ? a : colMinWidth );
                return result;
            })();
            (function(){
                var cssSyntax = '';
                for(colIndex=0;colIndex<=colMaxIndex;colIndex++) {
                    const colClass = `mdmreport-colindex-${colIndex}`;
                    const widthRaw = `${( isFinite(colWidthsAdjusted[colIndex]) && (colWidthsAdjusted[colIndex]>colMaxAllowedWidth) ? colMaxAllowedWidth : colWidthsAdjusted[colIndex] )}`;
                    const widthVal = `${widthRaw}px`;
                    cssSyntax = cssSyntax + ` .${colClass} { width: ${widthVal}!important; max-width: ${widthVal}!important; } `;
                }
                cssSheet.replaceSync(cssSyntax);
            })();
            Array.prototype.forEach.call(tables_all,function(tableEl,tableIndex) {
                //const rowElements = tableEl.querySelectorAll('tr.mdmreport-record');
                //Array.prototype.forEach.call(rowElements,function(rowElement,tableIndex) {
                //    colElements = rowElement.querySelectorAll('tr.mdmreport-record>td');
                //    Array.prototype.forEach.call(colElements,function(colEl,colIndex) {
                //        colEl.width = colWidthsAdjusted[colIndex];
                //    });
                //});
                tableEl.classList.add('mdmreport-table-formatting-fixeddimensions');
            });
        } catch(e) {
            printErrors(e);
            throw e;
        }
    };
    const dispatchDelayedEventData = {
        promise: null
    };
    function processDelayed() {
        if(!!dispatchDelayedEventData.promise) {
            /* setTimeout(resolve,40); */
        } else {
            dispatchDelayedEventData.promise = new Promise((resolve,reject)=>{
                setTimeout(resolve,40);
            });
            dispatchDelayedEventData.promise.then(()=>{
                dispatchDelayedEventData.promise = null;
                return process();
            });
        }
    }
    window.addEventListener('resize',wrapErrors(processDelayed));
    window.addEventListener('mdmtable',wrapErrors(processDelayed));
    document.addEventListener('mdmdocument',wrapErrors(processDelayed));
}
alignColWidthsInit();

