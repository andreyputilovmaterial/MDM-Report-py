function dispatchEvents() {
    Promise.resolve().then( function() { window.dispatchEvent(new Event('mdmdocument')); } );
    Promise.resolve().then( function() { window.dispatchEvent(new Event('mdmtable')); } );
}
window.addEventListener('DOMContentLoaded',dispatchEvents);
