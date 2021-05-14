define([
    'base/js/namespace',
    'jquery',
    'base/js/events',
], function (Jupyter, $, events) {
    const API_ROUTE = "/pretty-python-server/pretty-code";

    /*
        Returns html-markup from latex-markup using MathJax
        @param latex - latex markup
        @returns string
     */
    function extract_html(latex) {
        //ToDo
        throw new Error("Not implemented exception!");
    }

    /*
       Change raw python code on pretty math pseudo-code
       @param cell - cell with python code
       @returns Promise<void>
    */
    async function make_python_pretty(cell) {
        const latex_markup = await get_latex_markup_from_code(cell.get_text());
        const code_wrapper = cell.code_mirror.display.lineDiv;

        const html = extract_html(latex_markup);
        $(code_wrapper).html(
            '<pre class=" CodeMirror-line " role="presentation">'
            + html +
            '</pre>'
        );

    }

    /*
       Returns latex markup from cell python code
       @param code - python source code
       @returns Promise<string>
    */
    async function get_latex_markup_from_code(code) {
        const _get_cookie = name => {
            const r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        }

        const config = {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {'Content-Type': 'application/json', "X-XSRFToken": _get_cookie('_xsrf')},
            body: JSON.stringify({code})
        };

        const json = await fetch(API_ROUTE, config)
            .then(p => p.json())
            .catch(e => console.error(e));

        return json['latex_code'];
    }

    /*
        Run on start
     */
    async function load_ipython_extension() {
        events.on("execute.CodeCell", async (event, data) => {
            await make_python_pretty(data.cell);
        });
    }

    return {load_ipython_extension};
});