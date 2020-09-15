// events constants
let TIMER_EVENT = 'time', NEW_MAZE_EVENT = 'new_maze', NEW_COORD_EVENT = 'new_coord',
    GAME_OVER_EVENT = 'game_over', ERROR_EVENT = 'error', MOVE_EVENT = 'move', NAME_EVENT = 'name';
// colors
let USER_COLOR = 'black', FINISH_COLOR = '#bd0000', WALL_COLOR = '#5ad654';
// access move directions
let RIGHT = 'r', LEFT = 'l', TOP = 't', BOTTOM = 'b';

// variable for lock keyboard while access only one path
let is_lock_key = true;
// moveFunc - setInterval func, moveTo - next move direction for setInterval
let moveFunc, moveTo;

let canvas = document.getElementById('MazeCanvas');
ctx = canvas.getContext('2d');
ctx.lineWidth = 5;
let width = canvas.width, height = canvas.height;

// maze variable
let matrix, current_x, current_y, max_depth_x, max_depth_y;

let wsUri = (window.location.protocol == 'https:' && 'wss://' || 'ws://') + window.location.host + '/api/v1/ws/maze';
let conn = new WebSocket(wsUri);

conn.onmessage = function(e) {
    let parsed_data = JSON.parse(e.data)

    switch (parsed_data['event']) {
        case NEW_MAZE_EVENT: {
            // repaint maze

            // stop movement (setInterval)
            clearInterval(moveFunc);

            // change score
            let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Score: (\d+);/, `Score: ${parsed_data['content']['score']};`)
            document.getElementsByClassName('info')[0].innerHTML = new_html;

            paintMazeEvent(parsed_data['content']['maze']);
            is_lock_key = false;
            break;
        }
        case NEW_COORD_EVENT: {
            // if out of sync with server, make a lock until coordinates are verified
            break;
        }
        case TIMER_EVENT: {
            // update timer
            let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Time: (\d+);/, `Time: ${parsed_data['content']};`)
            document.getElementsByClassName('info')[0].innerHTML = new_html;
            break;
        }
        case GAME_OVER_EVENT: {
            // Game over. Stop game movement, require and send name.

            is_lock_key = true;
            clearInterval(moveFunc);

            // on server also exist validation
            // if clicked 'cancel', name == undefined
            let name = prompt('Enter your name (max length = 20)');
            while (name && name.length > 20) {
                name = prompt('Length > 20');
            }
            if (name) {
                json = JSON.stringify({'event': NAME_EVENT, 'content': name});
                conn.send(json);
            }
             window.location.href = '/';
            break;
        }
        case ERROR_EVENT: {
            console.error(parsed_data)
            break;
        }
    }
};
conn.onopen = function(e) {};
conn.onclose = function(e) {};

function paintMazeEvent(maze_obj) {
    // Paint new maze and update variables

    matrix = maze_obj['matrix'];
    current_x = maze_obj['current_x'],  current_y = maze_obj['current_y'];
    max_depth_x = maze_obj['max_depth_x'], max_depth_y = maze_obj['max_depth_y'];

	let RowCount = matrix.length;
	let ColCount = matrix[0].length;
	let size_cells = width / RowCount;

    // update size record
    let new_html = document.getElementsByClassName('info')[0].innerHTML.replace(/Size: (\d+)x(\d+);/, `Size: ${RowCount}x${ColCount};`)
    document.getElementsByClassName('info')[0].innerHTML = new_html;

    ctx.clearRect(0, 0, width, height);
    ctx.beginPath();

    // paint user-rectangle
	ctx.fillStyle = USER_COLOR;
    ctx.fillRect(size_cells / 4 + current_x * size_cells, size_cells / 4 + current_y * size_cells, size_cells / 2, size_cells / 2);
    // paint finish rectangle
    ctx.fillStyle = FINISH_COLOR;
    ctx.fillRect(size_cells / 4 + max_depth_x * size_cells, size_cells / 4 + max_depth_y * size_cells, size_cells / 2, size_cells / 2);

    // paint walls
	ctx.strokeStyle = WALL_COLOR;
	for (let y = 0; y < RowCount; y++)
	{
		for (let x = 0; x < ColCount; x++)
		{
			if(matrix[y][x][RIGHT])
			{
				ctx.moveTo(size_cells * (x + 1), size_cells * y);
				ctx.lineTo(size_cells * (x + 1), size_cells * (y + 1));
			}
			if(matrix[y][x][LEFT])
			{
				ctx.moveTo(size_cells * x, size_cells * y);
				ctx.lineTo(size_cells * x, size_cells * (y + 1));
			}
			if(matrix[y][x][TOP])
			{
				ctx.moveTo(size_cells * x, size_cells * y);
				ctx.lineTo(size_cells * (x + 1), size_cells * y);
			}
			if(matrix[y][x][BOTTOM])
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
    KeyDown event

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
        // lock keyboard while exist only one path...
        is_lock_key = true;
        switch (e.keyCode)
        {
            case 68:
            case 39: {
                moveTo = RIGHT;
                json = JSON.stringify({'event': MOVE_EVENT, 'content': moveTo});
                conn.send(json);
                // ...and go to this path. Lock be off in GoTo func or after 'new_maze' message
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
            case 65:
            case 37: {
                moveTo = LEFT;
                json = JSON.stringify({'event': MOVE_EVENT, 'content': moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
            case 87:
            case 38: {
                moveTo = TOP;
                json = JSON.stringify({'event': MOVE_EVENT, 'content': moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
            case 83:
            case 40: {
                moveTo = BOTTOM;
                json = JSON.stringify({'event': MOVE_EVENT, 'content': moveTo});
                conn.send(json);
                moveFunc = setInterval('GoTo(moveTo)', 50);
                break;
            }
        }
    }
}

function getAccessPaths() {
    // get all path where not wall
    return [RIGHT, LEFT, TOP, BOTTOM].filter(path => !matrix[current_y][current_x][path]);
}

function GoTo(path) {
    // function for move rectangle on one cell and stop setInterval-func if needed

    let accessPaths = getAccessPaths();
    if (!accessPaths.includes(path)) {
        is_lock_key = false;
        clearInterval(moveFunc);
        return;
    }

    let RowCount = matrix.length;
    let ColCount = matrix[0].length;
    let size_cells = width / RowCount;
    // clear old user-rectangle
    ctx.clearRect(size_cells / 5 + current_x * size_cells, size_cells / 5 + current_y * size_cells,
                  size_cells / 1.6, size_cells / 1.6);

    // change coordinate and collect access path except path from where come
    switch (path)
    {
        case RIGHT: {
            current_x++;
            accessPaths = getAccessPaths();
            accessPaths = accessPaths.filter(x => x != LEFT);
            break;
        }
        case LEFT: {
            current_x--;
            accessPaths = getAccessPaths();
            accessPaths = accessPaths.filter(x => x != RIGHT);
            break;
        }
        case TOP: {
            current_y--;
            accessPaths = getAccessPaths();
            accessPaths = accessPaths.filter(x => x != BOTTOM);
            break;
        }
        case BOTTOM: {
            current_y++;
            accessPaths = getAccessPaths();
            accessPaths = accessPaths.filter(x => x != TOP);
            break;
        }
    }
    // paint user-rectangle by new coordinates
    ctx.fillStyle = USER_COLOR;
    ctx.fillRect(size_cells / 4 + current_x * size_cells, size_cells / 4 + current_y * size_cells, size_cells / 2, size_cells / 2);

    // If finish, lock keyboard and wait server response (will be come 'new_maze' message if all message send right)
    if (current_x == max_depth_x && max_depth_y == current_y) {
        clearInterval(moveFunc);
        return;
    }

    // if count paths > 1 (except path from where come) or 0 (dead end), then unlock keyboard and stop moveFunc
    if (accessPaths.length != 1) {
        is_lock_key = false;
        clearInterval(moveFunc);
    }
    moveTo = accessPaths[0];
}

addEventListener('keydown', GetKeyCode);
