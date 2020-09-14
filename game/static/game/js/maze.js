let TIMER_EVENT = 'time', NEW_MAZE_EVENT = 'new_maze', NEW_COORD_EVENT = 'new_coord',
    GAME_OVER_EVENT = 'game_over', ERROR_EVENT = 'error', MOVE_EVENT = 'move', NAME_EVENT = 'name';
let USER_COLOR = 'black', FINISH_COLOR = '#bd0000', WALL_COLOR = '#5ad654';
let RIGHT = 'r', LEFT = 'l', TOP = 't', BOTTOM = 'b';

let is_lock_key = true, moveFunc, moveTo;

let canvas = document.getElementById("MazeCanvas");
ctx = canvas.getContext('2d');
ctx.lineWidth = 5;
let width = canvas.width, height = canvas.height;

let matrix, current_x, current_y, max_depth_x, max_depth_y;

let wsUri = (window.location.protocol == 'https:' && 'wss://' || 'ws://') + window.location.host + '/api/v1/ws/maze';
let conn = new WebSocket(wsUri);

conn.onmessage = function(e) {
    let parsed_data = JSON.parse(e.data)

    switch (parsed_data['event']) {
        case NEW_MAZE_EVENT: {
            console.log(parsed_data)
            clearInterval(moveFunc);

            let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Score: (\d+);/, `Score: ${parsed_data['data']['score']};`)
            document.getElementsByClassName('info')[0].innerHTML = new_html;
            paintMazeEvent(parsed_data['data']['maze']);
            is_lock_key = false;
            break;
        }
        case NEW_COORD_EVENT: {
            console.log(parsed_data)
            break;
        }
        case TIMER_EVENT: {
            console.log(parsed_data)
            let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Time: (\d+);/, `Time: ${parsed_data['data']};`)
            document.getElementsByClassName('info')[0].innerHTML = new_html;
            break;
        }
        case GAME_OVER_EVENT: {
            console.log(parsed_data)
            is_lock_key = true;
            clearInterval(moveFunc);

            let name = prompt("Enter your name (max length = 20)");
            while (name && name.length > 20) {
                name = prompt("Length > 20");
            }
            if (name) {
                json = JSON.stringify({"event": NAME_EVENT, "data": name});
                conn.send(json);
            }
             window.location.href = '/';
            break;
        }
        case ERROR_EVENT: {
            console.log(parsed_data)
            alert(parsed_data['data'])
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
    matrix = maze_obj['matrix'];
    current_x = maze_obj['current_x'],  current_y = maze_obj['current_y'];
    max_depth_x = maze_obj['max_depth_x'], max_depth_y = maze_obj['max_depth_y'];

	let RowCount = matrix.length;
	let ColCount = matrix[0].length;
	let size_cells = width / RowCount;

    let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Size: (\d+)x(\d+);/, `Size: ${RowCount}x${ColCount};`)
    document.getElementsByClassName('info')[0].innerHTML = new_html;

    ctx.clearRect(0, 0, width, height);
    ctx.beginPath();

	ctx.fillStyle = USER_COLOR;
    ctx.fillRect(size_cells / 4 + current_x * size_cells, size_cells / 4 + current_y * size_cells, size_cells / 2, size_cells / 2);
    ctx.fillStyle = FINISH_COLOR;
    ctx.fillRect(size_cells / 4 + max_depth_x * size_cells, size_cells / 4 + max_depth_y * size_cells, size_cells / 2, size_cells / 2);
	ctx.strokeStyle = WALL_COLOR;
	for (let y = 0; y < RowCount; y++)
	{
		for (let x = 0; x < ColCount; x++)
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

function GetKeyCode(e)
{
    /*
    d - 68
    right 39

    a - 65
    left 37

    w - 87
    up - 38

    s - 83
    down - 40
    */
    if(matrix && !is_lock_key && [68, 87, 83, 65, 39, 37, 40, 38].includes(e.keyCode))
    {
        is_lock_key = true;
        switch (e.keyCode)
        {
            case 68:
            case 39: {
                moveTo = RIGHT;
                json = JSON.stringify({"event": MOVE_EVENT, "data": moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
            case 65:
            case 37: {
                moveTo = LEFT;
                json = JSON.stringify({"event": MOVE_EVENT, "data": moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
            case 87:
            case 38: {
                moveTo = TOP;
                json = JSON.stringify({"event": MOVE_EVENT, "data": moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
            case 83:
            case 40: {
                moveTo = BOTTOM;
                json = JSON.stringify({"event": MOVE_EVENT, "data": moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
        }
    }
}

function getAccessWays() {
    accessWays = [];
    if (!matrix[current_y][current_x][RIGHT]) {
        accessWays.push(RIGHT);
    }
    if (!matrix[current_y][current_x][LEFT]) {
        accessWays.push(LEFT);
    }
    if (!matrix[current_y][current_x][TOP]) {
        accessWays.push(TOP);
    }
    if (!matrix[current_y][current_x][BOTTOM]) {
        accessWays.push(BOTTOM);
    }
    return accessWays;
}

function GoTo(way) {
    let accessWays = getAccessWays();
    if (!accessWays.includes(way)) {
        is_lock_key = false;
        clearInterval(moveFunc);
        return;
    }

    let RowCount = matrix.length;
    let ColCount = matrix[0].length;
    let size_cells = width / RowCount;
    ctx.clearRect(size_cells / 5 + current_x * size_cells, size_cells / 5 + current_y * size_cells, size_cells / 1.6, size_cells / 1.6);

    switch (way)
    {
        case RIGHT: {
            current_x++;
            accessWays = getAccessWays();
            accessWays = accessWays.filter(x => x != LEFT);
            break;
        }
        case LEFT: {
            current_x--;
            accessWays = getAccessWays();
            accessWays = accessWays.filter(x => x != RIGHT);
            break;
        }
        case TOP: {
            current_y--;
            accessWays = getAccessWays();
            accessWays = accessWays.filter(x => x != BOTTOM);
            break;
        }
        case BOTTOM: {
            current_y++;
            accessWays = getAccessWays();
            accessWays = accessWays.filter(x => x != TOP);
            break;
        }
    }
    ctx.fillStyle = USER_COLOR;
    ctx.fillRect(size_cells / 4 + current_x * size_cells, size_cells / 4 + current_y * size_cells, size_cells / 2, size_cells / 2);

    if (current_x == max_depth_x && max_depth_y == current_y) {
        is_lock_key = true;
        clearInterval(moveFunc);
        return;
    }

    if (accessWays.length != 1) {
        is_lock_key = false;
        clearInterval(moveFunc);
    }
    moveTo = accessWays[0];
}

addEventListener("keydown", GetKeyCode);
