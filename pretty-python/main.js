define([
    'base/js/namespace',
    'jquery',
    'base/js/events',
], function (Jupyter, $, events) {
    const apiRoute = "/pretty-python-server/pretty-code"

    function _get_cookie(name) {
        const r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }

    async function make_python_pretty(cell) {
        const html = await get_pretty_html_from_code(cell.get_text());
        const code_wrapper = cell.code_mirror.display.lineDiv;
        if (cell.get_text() === "c = a * b") {
            $(code_wrapper).html(
                '<pre class=" CodeMirror-line " role="presentation">' + html.join(' ') + '</pre>'
            );
        }
    }

    async function get_pretty_html_from_code(code) {
        const config = {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {'Content-Type': 'application/json', "X-XSRFToken": _get_cookie('_xsrf')},
            body: JSON.stringify({code})
        };
        const json = await fetch(apiRoute, config)
            .then(p => p.json())
            .catch(e => console.error(e));
        return [
            '<span class="cm-variable">c</span>',
            '<span class="cm-operator">=</span>',
            '<span class="cm-variable">a</span>',
            '<span class="cm-operator">⋅</span>',
            '<span class="cm-variable">b</span>',
        ];
    }

    // Run on start
    async function load_ipython_extension() {
        events.on("execute.CodeCell", async (event, data) => {
            await make_python_pretty(data.cell);
        });
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});