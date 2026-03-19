window.MathJax = {
    tex: {
        inlineMath: [['\\(', '\\)']],
        displayMath: [['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true,
    },
    options: {
        ignoreHtmlClass: '.*|',
        processHtmlClass: 'arithmatex',
    },
}

document$.subscribe(async () => {
    if (!window.MathJax?.startup?.promise || !window.MathJax?.startup?.output) {
        return
    }
    await window.MathJax.startup.promise
    MathJax.startup.output.clearCache()
    MathJax.typesetClear()
    MathJax.texReset()
    await MathJax.typesetPromise()
})
