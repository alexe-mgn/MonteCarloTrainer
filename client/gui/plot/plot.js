const PLOT_ID = 'plot';

const COLOR = {
    function: 'blue',
    rect: '',
    rect_fill: 'rgba(0,255,0,0.25)',
    point: 'orange',
    point_select: 'red'
}

let plot_function_data = {
    x: [],
    y: [],
    line: {color: COLOR.function},
    name: 'функция'
}
let plot_points_data = {
    x: [],
    y: [],
    marker: {size: 10, color: []},
    mode: 'markers',
    name: 'точки'
}
let selected_point = null
let plot_data = [
    plot_function_data,
    plot_points_data
]

let plot_rect_data = {
    x0: 0, x1: 0,
    y0: 0, y1: 0,
    fillcolor: COLOR.rect,
    type: 'rect',
    xref: 'x',
    yref: 'y',
    visible: true,
    layer: 'below'
}
let plot_layout = {
    showlegend: false,
    margin: {l: 0, r: 0, b: 0, t: 0, pad: 0},
    // autosize: true,
    shapes: [
        plot_rect_data
    ]
}


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
        plot_data,
        plot_layout,
        {responsive: true}
    )
}


function updatePlot() {
    Plotly.redraw(PLOT_ID)
}

window.updatePlot = updatePlot


export function adjustSize() {
    Plotly.Plots.resize(PLOT_ID)
}

window.adjustSize = adjustSize


export function resetPlotData() {
    plot_function_data.x = []
    plot_function_data.y = []
    plot_function_data.line.color = COLOR.function
    plot_rect_data.x0 = 0
    plot_rect_data.x1 = 0
    plot_rect_data.y0 = 0
    plot_rect_data.y1 = 0
    plot_rect_data.fillcolor = COLOR.rect
    plot_points_data.x = []
    plot_points_data.y = []
    plot_points_data.marker.color = []
    selected_point = null
}

window.resetPlotData = resetPlotData


export function setFunctionPlot(xs, ys) {
    plot_function_data.x = xs
    plot_function_data.y = ys
}

window.setFunctionPlot = setFunctionPlot


export function setRect(x0, x1, y0, y1) {
    plot_rect_data.x0 = x0
    plot_rect_data.x1 = x1
    plot_rect_data.y0 = y0
    plot_rect_data.y1 = y1
}

window.setRect = setRect


export function setRectFill(fill) {
    plot_rect_data.fillcolor = fill ? COLOR.rect_fill : COLOR.rect
}

window.setRectFill = setRectFill


export function addPoint(x, y) {
    let color = plot_points_data.marker.color
    plot_points_data.x.push(x)
    plot_points_data.y.push(y)
    color.push(COLOR.point)
}

window.addPoint = addPoint


export function setPoints(xs, ys) {
    plot_points_data.x = xs
    plot_points_data.y = ys
    plot_points_data.marker.color = Array(xs.length).fill(COLOR.point)
}

window.setPoints = setPoints


export function selectPoint(index) {
    let color = plot_points_data.marker.color
    if (selected_point !== null)
        color[selected_point] = COLOR.point
    if (index !== null)
        color[index] = COLOR.point_select
    selected_point = index
}

window.selectPoint = selectPoint


document.addEventListener('DOMContentLoaded', initPlot)
// document.addEventListener('DOMContentLoaded', test)
