define([
    'base/js/namespace',
    'jquery',
    'base/js/events',
], function (Jupyter, $, events) {

    /*
        Change raw python code on pretty math pseudo-code
        @param cell - cell with python code
     */
    function make_python_pretty(cell) {
        const html = get_pretty_html_from_code(cell.get_text());
        const code_wrapper = cell.code_mirror.display.lineDiv;
        $(code_wrapper).html(
            '<pre class=" CodeMirror-line " role="presentation">' +
                html.join(' ') +
            '</pre>'
        );
    }

    /*
       Returns wrapped html pretty math code from raw python code
       @param code - python source code
    */
    function get_pretty_html_from_code(code) {
        return [
            '<span class="cm-variable">c</span>',
            '<span class="cm-operator">=</span>',
            '<span class="cm-variable">10</span>',
            '<span class="cm-operator">⋅</span>',
            '<span class="cm-variable">12</span>',
        ];
    }

    // Run on start
    function load_ipython_extension() {
        events.on("execute.CodeCell", function (event, data) {
            console.log(data.cell);
            make_python_pretty(data.cell);
        });
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});