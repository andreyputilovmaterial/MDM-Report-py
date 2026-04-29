/* === add diff classes to the begginning of every line in pre tags in the report plugin === */
function init() {
    function initUpdateLines() {
        
        function checkClassesIndicatingEdit(el) {
            return Array.from(el.querySelectorAll('.mdmdiff-inlineoverlay-added, .mdmdiff-inlineoverlay-removed')).length>0;
        }
        function checkClassesIndicatingEditAdded(el) {
            return Array.from(el.querySelectorAll('.mdmdiff-inlineoverlay-added')).length>0;
        }
        function checkClassesIndicatingEditRemoved(el) {
            return Array.from(el.querySelectorAll('.mdmdiff-inlineoverlay-removed')).length>0;
        }

        function wrapLinesInParagraphs(container) {
            // warning: code suggested by chatgpt
            const wrapper = container.cloneNode(false);
        
            let currentP = document.createElement('p');
            wrapper.appendChild(currentP);
        
            // Stack to track nesting of inline tags
            const stack = [];
        
            function cloneStack() {
            let parent = currentP;
            stack.forEach(originalNode => {
                const clone = originalNode.cloneNode(false);
                parent.appendChild(clone);
                parent = clone;
            });
            return parent; // Deepest nested element
            }
        
            function processNode(node, currentParent) {
            if (node.nodeType === Node.TEXT_NODE) {
                currentParent.appendChild(node.cloneNode());
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.tagName === 'BR') {
                // Start new <p> on <br>
                currentP = document.createElement('p');
                wrapper.appendChild(currentP);
                const newDeepest = cloneStack(); // Reopen nested inline tags
                return newDeepest;
                } else {
                const clone = node.cloneNode(false);
                currentParent.appendChild(clone);
                stack.push(node); // Push original node to stack
                let childParent = clone;
        
                node.childNodes.forEach(child => {
                    childParent = processNode(child, childParent) || childParent;
                });
        
                stack.pop(); // Pop after done
                }
            }
            return currentParent;
            }
        
            container.childNodes.forEach(node => {
                processNode(node, currentP);
            });
        
            return wrapper;
        }
                    
        Array.from(document.querySelectorAll('.mdmreport-table tr td pre')).forEach(function(elPreOriginal){
            
            const elPreUpdated = wrapLinesInParagraphs(elPreOriginal);
            elPreOriginal.replaceWith(elPreUpdated);

            Array.from(elPreUpdated.querySelectorAll('p')).forEach(function(elP){
                if(checkClassesIndicatingEdit(elP)) {
                    elP.classList.add('mdmreport-l-c');
                }
                if(checkClassesIndicatingEditAdded(elP)) {
                    elP.classList.add('mdmreport-l-a');
                }
                if(checkClassesIndicatingEditRemoved(elP)) {
                    elP.classList.add('mdmreport-l-r');
                }
            });

        });
    }
    function initAddControls() {
        Array.from(document.querySelectorAll('.mdmreport-table tr td pre')).forEach(function(elPre) {
            
            if( Array.from(elPre.querySelectorAll('.mdmreport-precontrolplugin-control, .mdmreport-precontrolplugin-control-prev, .mdmreport-precontrolplugin-control-next')).length>0 ) return;
            
            const data = {
                elPre: elPre,
                activeRowEl: null,
                allRowEls: [],
                visible: false,
                controlPrevEl: null,
                controlNextEl: null,
                visibilityTriggerers: 0
            };
            function scrollToElementCenter(element) {
                const elementRect = element.getBoundingClientRect();
                const elementTop = elementRect.top + window.scrollY;
                const elementHeight = elementRect.height;
                const viewportHeight = window.innerHeight;
                const scrollTo = elementTop - (viewportHeight / 2) + (elementHeight / 2);
                window.scrollTo({ top: scrollTo, behavior: 'smooth' });
            }
            function getPrev(el) {
                if( !el || !data.allRowEls ) return;
                const indexActive = data.allRowEls.indexOf(el);
                if( indexActive<0 ) return;
                const elSwitchTo = indexActive>=1 ? data.allRowEls[indexActive-1] : null;
                return elSwitchTo;
            }
            function getNext(el) {
                if( !el || !data.allRowEls ) return;
                const indexActive = data.allRowEls.indexOf(el);
                if( indexActive<0 ) return;
                const elSwitchTo = indexActive<data.allRowEls.length-1 ? data.allRowEls[indexActive+1] : null;
                return elSwitchTo;
            }
            function scrollPrev() {
                const elSwitchTo = getPrev(data.activeRowEl);
                if( !elSwitchTo ) return;
                console.log(`this one: "${data.activeRowEl.innerText}", switch to (prev): "${elSwitchTo.innerText}"`);
                scrollToElementCenter(elSwitchTo);
                handleHover(({target:elSwitchTo}));
            }
            function scrollNext() {
                const elSwitchTo = getNext(data.activeRowEl);
                if( !elSwitchTo ) return;
                console.log(`this one: "${data.activeRowEl.innerText}", switch to (next): "${elSwitchTo.innerText}"`);
                scrollToElementCenter(elSwitchTo);
                handleHover(({target:elSwitchTo}));
            }
            function updatePosition() {
                data.controlPrevEl.style.top = `${data.activeRowEl.offsetTop-data.controlPrevEl.offsetHeight*1.25}px`;
                data.controlNextEl.style.top = `${data.activeRowEl.offsetTop+data.activeRowEl.offsetHeight+data.controlNextEl.offsetHeight*0.25}px`;
                if( !!getPrev(data.activeRowEl) ) { data.controlPrevEl.style.visibility = 'visible'; } else { data.controlPrevEl.style.visibility = 'hidden'; };
                if( !!getNext(data.activeRowEl) ) { data.controlNextEl.style.visibility = 'visible'; } else { data.controlNextEl.style.visibility = 'hidden'; };
            }
            function handleChange(newRowEl) {
                if( newRowEl===data.activeRowEl ) {
                    /* no action needed */
                } else {
                    data.activeRowEl = newRowEl;
                    updatePosition();
                }
            };
            function checkVisibility() {
                if( !data.controlPrevEl || !data.controlNextEl ) return;
                if( data.visibilityTriggerers>0 ) {
                    if( !data.visible ) {
                        data.controlPrevEl.style.display = 'block';
                        data.controlNextEl.style.display = 'block';
                    }
                    data.visible = true;
                } else {
                    if( !!data.visible ) {
                        data.controlPrevEl.style.display = 'none';
                        data.controlNextEl.style.display = 'none';
                    }
                    data.visible = false;
                }
            }
            function updateVisibility() {
                setTimeout(function(){
                    const promise = new Promise(function(resolve,reject){data.visibilityTriggerers+=1;checkVisibility();setTimeout(resolve,3000)});
                    promise.then(function(){data.visibilityTriggerers-=1;checkVisibility();});
                },400);
            }
            function handleHover(event) {
                const el = event.target;
                handleChange(el);
                updateVisibility();
            }

            const elAddControlPrev = document.createElement('div');
            const elAddControlNext = document.createElement('div');
            elAddControlPrev.classList.add('mdmreport-precontrolplugin-control','mdmreport-precontrolplugin-control-prev');
            elAddControlNext.classList.add('mdmreport-precontrolplugin-control','mdmreport-precontrolplugin-control-next');
            elAddControlPrev.innerHTML = '&#x25B2;';
            elAddControlNext.innerHTML = '&#x25BC;';
            elAddControlPrev.addEventListener('click',wrapErrors(function(event){event.preventDefault();return scrollPrev()&&false;}));
            elAddControlNext.addEventListener('click',wrapErrors(function(event){event.preventDefault();return scrollNext()&&false;}));
            data.controlPrevEl = elAddControlPrev;
            data.controlNextEl = elAddControlNext;
            data.allRowEls = Array.from(elPre.querySelectorAll('.mdmreport-l-c, .mdmreport-l-a, .mdmreport-l-r'));
            data.allRowEls.forEach(function(elRow){
                elRow.addEventListener('mouseover',wrapErrors(handleHover));
                data.allRowElements
            });
            elAddControlPrev.addEventListener('mouseover',wrapErrors(updateVisibility));
            elAddControlNext.addEventListener('mouseover',wrapErrors(updateVisibility));
            elPre.appendChild(elAddControlPrev);
            elPre.appendChild(elAddControlNext);

        });
    }
    try {
        initUpdateLines();
        initAddControls();
    } catch(e) {
        try {
            // undoSmth();
        } catch(e) { }
        printErrors(e);
        throw e;
    }
}
window.addEventListener('mdmdocument',wrapErrors(init));
window.addEventListener('mdmtable',wrapErrors(init));
