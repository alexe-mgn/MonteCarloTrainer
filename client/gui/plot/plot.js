const PLOT_ID = 'plot';


export function test() {
    let nS = 20
    let xSRange = [2, 7]
    let ySRange = [2, 7]
    let xS = Array.from({length: nS},
        () => (Math.random() * (xSRange[1] - xSRange[0]) + xSRange[0]))
    let yS = Array.from({length: nS},
        () => (Math.random() * (ySRange[1] - ySRange[0]) + ySRange[0]))

    Plotly.newPlot(
        PLOT_ID,
        [
            {
                'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'y': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            },
            {
                'x': xS,
                'y': yS,
                'mode': 'markers',
                marker: {size: 15}
            }
        ],
        {
            showlegend: false,
            shapes: [
                {
                    type: 'rect',
                    xref: 'x',
                    yref: 'y',
                    x0: 2, x1: 7,
                    y0: 2, y1: 7
                }
            ]
        },
        {responsive: true}
    )
    console.log('Testing 1 2 3.')
}

export function initPlot() {
    Plotly.newPlot(
        PLOT_ID,
        [
            {
                'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'y': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            }
        ],
        {autosize: true},
        {responsive: true}
    )
}


export function adjustSize() {
    Plotly.Plots.resize(PLOT_ID)
}


document.addEventListener('DOMContentLoaded', initPlot)
document.addEventListener('DOMContentLoaded', test)
window.test = test
window.adjustSize = adjustSize
