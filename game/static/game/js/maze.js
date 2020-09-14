let TIMER_EVENT = 'time', NEW_MAZE_EVENT = 'new_maze', NEW_COORD_EVENT = 'new_coord',
    GAME_OVER_EVENT = 'game_over', ERROR_EVENT = 'error';
let USER_COLOR = 'black', FINISH_COLOR = '#bd0000', WALL_COLOR = '#5ad654';

let canvas = document.getElementById("MazeCanvas");
ctx = canvas.getContext('2d');
ctx.lineWidth = 5;
let width = canvas.width, height = canvas.height;

let wsUri = (window.location.protocol == 'https:' && 'wss://' || 'ws://') + window.location.host + '/api/v1/ws/maze';
let conn = new WebSocket(wsUri);


conn.onmessage = function(e) {
    console.log(JSON.parse(e.data))
    let parsed_data = JSON.parse(e.data)

    switch (parsed_data['event']) {
        case NEW_MAZE_EVENT: {
            let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Score: (\d+);/, `Score: ${parsed_data['score']};`)
            document.getElementsByClassName('info')[0].innerHTML = new_html;
            paintMazeEvent(parsed_data['maze']);
            break;
        }
        case NEW_COORD_EVENT: {
            break;
        }
        case TIMER_EVENT: {
            let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Time: (\d+);/, `Time: ${parsed_data['time']};`)
            document.getElementsByClassName('info')[0].innerHTML = new_html;
            break;
        }
        case GAME_OVER_EVENT: {
            let name = prompt("Enter your name (max length = 20)");
            while (name.length > 20) {
                name = prompt("Length > 20");
            }
            console.log(name);
            break;
        }
        case ERROR_EVENT: {
            alert(parsed_data['message'])
            break;
        }
    }
};
conn.onopen = function(e) {
    console.log('open', e)
};
conn.onclose = function(e) {
    console.log('close', e)
};

function paintMazeEvent(maze_obj) {
    let matrix = maze_obj['matrix'];
    let start_x = maze_obj['current_x'],  start_y = maze_obj['current_y'];
    let max_depth_x = maze_obj['max_depth_x'], max_depth_y = maze_obj['max_depth_y'];

	let RowCount = matrix.length;
	let ColCount = matrix[0].length;
	let size_cells = width / RowCount;

    let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Size: (\d+)x(\d+);/, `Size: ${RowCount}x${ColCount};`)
    document.getElementsByClassName('info')[0].innerHTML = new_html;

    ctx.clearRect(0, 0, width, height);

	ctx.fillStyle = USER_COLOR;
    ctx.fillRect(size_cells/4 + start_x * size_cells, size_cells/4 + start_y * size_cells, size_cells/2, size_cells/2);
    ctx.fillStyle = FINISH_COLOR;
    ctx.fillRect(size_cells/4 + max_depth_x * size_cells, size_cells/4 + max_depth_y * size_cells, size_cells/2, size_cells/2);
	ctx.strokeStyle = WALL_COLOR;
	for (var y = 0; y < RowCount; y++)
	{
		for (var x = 0; x < ColCount; x++)
		{
			if(matrix[y][x]['r'])
			{
				ctx.moveTo(size_cells * (x + 1), size_cells * y);
				ctx.lineTo(size_cells * (x + 1), size_cells * (y + 1));
			}
			if(matrix[y][x]['l'])
			{
				ctx.moveTo(size_cells * x, size_cells * y);
				ctx.lineTo(size_cells * x, size_cells * (y + 1));
			}
			if(matrix[y][x]['t'])
			{
				ctx.moveTo(size_cells * x, size_cells * y);
				ctx.lineTo(size_cells * (x + 1), size_cells * y);
			}
			if(matrix[y][x]['b'])
			{
				ctx.moveTo(size_cells * x, size_cells * (y + 1));
				ctx.lineTo(size_cells * (x + 1), size_cells * (y + 1));
			}
		}
	}
	ctx.stroke();
}