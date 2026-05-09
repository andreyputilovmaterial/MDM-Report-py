function initAddControlBlock() {
    const isWithinDiffInDiff = document.body?.classList.contains('mdmdiff-in-diff') ?? false;
    if( !isWithinDiffInDiff) return;
    const pluginHolderEl = document.querySelector('#mdmreport_plugin_placeholder');
    if(!pluginHolderEl) throw new Error('adding block to show/hide columns: failed to find proper place for the element: #mdmreport_plugin_placeholder');
    const bannerEl = document.createElement('div');
    bannerEl.className = 'mdmreport-diffondiffcontrolblock-plugin mdmreport-banner';
    bannerEl.innerHTML = '<form method="_POST" action="#!" onSubmit="javascript: return false;" class="mdmreport-controls"><fieldset class="mdmreport-controls"><div><legend>Diff on diff: show all records:</legend></div></fieldset></form>';
    Array.prototype.forEach.call(bannerEl.querySelectorAll('form'),function(formEl) {formEl.addEventListener('submit',wrapErrors(function(event) {event.preventDefault();event.stopPropagation();return false;}));});
    const possiblyExistingEl = document.querySelector('.mdmreport-diffondiffcontrolblock-plugin');
    if( possiblyExistingEl ) {
        possiblyExistingEl.replaceWith(bannerEl);
    } else {
        pluginHolderEl.append(bannerEl);
    }

    const labelEl = document.createElement('label');
    labelEl.textContent = 'Show all records';
    labelEl.classList.add('mdmreport-controls');
    const checkboxEl = document.createElement('input');
    checkboxEl.setAttribute('type','checkbox');
    checkboxEl.setAttribute('checked','false');
    checkboxEl.checked = false;
    checkboxEl.addEventListener('change',wrapErrors(function(event) {
        const checkboxEl = event.target;
        if( checkboxEl.checked ) {
            Array.prototype.forEach.call(document.querySelectorAll('body'),function(tableEl) {
                tableEl.classList.add('mdmdiff-in-diff-show-all-records');
            });
        } else {
            Array.prototype.forEach.call(document.querySelectorAll('body'),function(tableEl) {
                tableEl.classList.remove('mdmdiff-in-diff-show-all-records');
            });
        };
    }));
    labelEl.prepend(checkboxEl);
    bannerEl.querySelector('fieldset').append(labelEl);
}
window.addEventListener('mdmdocument',wrapErrors(initAddControlBlock));
// window.addEventListener('mdmtable',wrapErrors(initAddControlBlock));
