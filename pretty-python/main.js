define([
    'base/js/namespace',
    'require',
    'jquery',
    'base/js/events',
], function (Jupyter, requirejs, $, events) {
    const API_ROUTE = "/pretty-python-server/pretty-code";

    /**
       Change raw python code on pretty math pseudo-code
       @param {CodeCell} cell - cell with python code
       @returns Promise
    */
    async function make_python_pretty(cell) {
        const latex = await get_latex_markup_from_code(cell.get_text());
        const code_wrapper = cell.code_mirror.display.lineDiv;
        const latex_node = document.createElement("DIV");
        latex_node.innerHTML = latex;
        code_wrapper.innerHTML = "";

        await MathJax.Hub.Queue(["Typeset", MathJax.Hub, latex_node]);
        const newParent = document.createElement("PRE");
        newParent.innerHTML = latex_node.innerHTML;
        code_wrapper.appendChild(newParent);
    }

    /**
       Returns latex markup from cell python code
       @param {string} code - python source code
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
    /**
     * Add CSS file
     *
     * @param {string} filename filename
     * @return void`
     */
    function load_css(filename) {
        const link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = requirejs.toUrl(filename);
        document.getElementsByTagName("head")[0].appendChild(link);
    }


    /**
        Run on start
     */
    async function load_ipython_extension() {
        load_css("./style.css");
        MathJax.Hub.Config({
            "HTML-CSS": {
              preferredFont: "STIX"
            }
        });
        events.on("execute.CodeCell", async (event, data) => {
            await make_python_pretty(data.cell);
        });
    }

    return {load_ipython_extension};
});