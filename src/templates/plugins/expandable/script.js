
    /* === expandable blocks plugin === */
function ellipsisAssignClickHandler() {
    const clickListener = function(event,el) {
        event.preventDefault();
        const content = el.dataset.ellipsis;
        const elNew = document.createElement('span');
        elNew.classList.add('mdmreport-ellipsis-unhidden');
        elNew.innerHTML = content;
        el.replaceWith(elNew);
        return false;
    }
    document.addEventListener('click',wrapErrors(function(event) {
        const el = event.target.closest('[data-role="ellipsis"]');
        if (!el) return;
        return clickListener(event,el);
    }));
    const beautifyEllipsis = function(el) {
        if( !el.matches('.mdmreport-txt-ellipsis') ) throw new Error('should be of .mdmreport-txt-ellipsis class!');
        el.classList.add('mdmreport-txt-ellipsis-enchanced');
        el.querySelector('.mdmreport-txt-ellipsis-1').classList.add('mdmreport-txt-ellipsis-start');
        el.querySelector('.mdmreport-txt-ellipsis-2').classList.add('mdmreport-txt-ellipsis-full');
        el.querySelector('.mdmreport-txt-ellipsis-3').classList.add('mdmreport-txt-ellipsis-end');
        Array.from(el.querySelectorAll('.mdmreport-txt-ellipsis-br')).forEach(function(i){i.remove();})
    }
}
window.addEventListener('mdmdocument',wrapErrors(ellipsisAssignClickHandler));
// window.addEventListener('mdmtable',wrapErrors(ellipsisAssignClickHandler));
