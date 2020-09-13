let wsUri = (window.location.protocol == 'https:' && 'wss://' || 'ws://') + window.location.host + '/api/v1/ws/maze';
let conn = new WebSocket(wsUri);
conn.onmessage = function(e) {
    let matrix = JSON.parse(e.data)['maze']['matrix'];
    let x_start = JSON.parse(e.data)['maze']['x_start']
    let y_start = JSON.parse(e.data)['maze']['y_start']
    let x_max_depth = JSON.parse(e.data)['maze']['x_max_depth']
    let y_max_depth = JSON.parse(e.data)['maze']['y_max_depth']
    canv = document.getElementById("MazeCanvas");
	context = canv.getContext('2d');
	context.lineWidth = 5;

    let width = height = 750;
	let RowCount = matrix.length;
	let ColCount = matrix[0].length;

	let size_cells = width / RowCount;

	context.fillStyle = "#3e8252";
    context.fillRect(size_cells/4 + x_start * size_cells, size_cells/4 + y_start * size_cells, size_cells/2, size_cells/2);
    context.fillStyle = "#bd0000";
    context.fillRect(size_cells/4 + x_max_depth * size_cells, size_cells/4 + y_max_depth * size_cells, size_cells/2, size_cells/2);
    context.fillStyle = "black";
	context.strokeStyle = "#5ad654";
	for (var y = 0; y < RowCount; y++)
	{
		for (var x = 0; x < ColCount; x++)
		{
			if(matrix[y][x]['r'])
			{
				context.moveTo(size_cells * (x + 1), size_cells * y);
				context.lineTo(size_cells * (x + 1), size_cells * (y + 1));
			}
			if(matrix[y][x]['l'])
			{
				context.moveTo(size_cells * x, size_cells * y);
				context.lineTo(size_cells * x, size_cells * (y + 1));
			}
			if(matrix[y][x]['t'])
			{
				context.moveTo(size_cells * x, size_cells * y);
				context.lineTo(size_cells * (x + 1), size_cells * y);
			}
			if(matrix[y][x]['b'])
			{
				context.moveTo(size_cells * x, size_cells * (y + 1));
				context.lineTo(size_cells * (x + 1), size_cells * (y + 1));
			}
		}
	}
	context.stroke();

};
conn.onopen = function(e) {
    console.log('open', e)
};
conn.onclose = function(e) {
    console.log('close', e)
};
