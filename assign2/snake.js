const GAME_BOARD_BORDER = "red";
const GAME_BOARD_COLOR = "black";
const SNAKE_COLOR = "red";
const SNAKE_BORDER_COLOR = "yellow";

var gameBoard = document.getElementById("gameBoard");

// a 2d drawing context
var ctx = gameBoard.getContext("2d");

function clearBoard() {
	ctx.fillStyle = GAME_BOARD_COLOR;
	ctx.strokestyle = GAME_BOARD_BORDER;

	ctx.fillRect(0,0,gameBoard.width, gameBoard.height);
	ctx.strokeRect(0,0, gameBoard.width, gameBoard.height);
}

let snake = [
	{x: 150, y: 150}, // SnakeHead
	{x: 140, y: 150},
	{x: 130, y: 150},
	{x: 120, y: 150},
];


function drawSnake() {
	snake.forEach( drawSnakePart);
}

function drawFood() {
	ctx.fillStyle = "yellow";
	ctx.strokestyle = "lightyellow";
	ctx.fillRect( foodX, foodY, 10, 10);
	ctx.strokeRect( foodX, foodY, 10, 10);
}

function drawSnakePart( snakePart) {
	ctx.fillStyle = SNAKE_COLOR;
	ctx.strokestyle = SNAKE_BORDER_COLOR;

	ctx.fillRect( snakePart.x, snakePart.y, 10, 10);
	ctx.strokeRect( snakePart.x, snakePart.y, 10, 10);
}

function advanceSnake()  {
	const head = { x: snake[0].x + dx_g, y: snake[0].y + dy_g };
	snake.unshift( head);

	const didEatFood = snake[0].x === foodX && snake[0].y === foodY;
	if ( didEatFood) {
		score_g += 1;
		document.getElementById("score").innerHTML = score_g;
		createFood();
	}
	else
		snake.pop();
}

function changeDirection( keyPressed) {
	if ( changingDirection)
		return;

    const LEFT_KEY = 37;
    const RIGHT_KEY = 39;
    const UP_KEY = 38;
    const DOWN_KEY = 40;

	changingDirection = true;

    //const keyPressed = event.keyCode;
    const goingUp = dy_g === -10;
    const goingDown = dy_g === 10;
    const goingRight = dx_g === 10;
    const goingLeft = dx_g === -10;

    if (keyPressed === LEFT_KEY && !goingRight) {
		dx_g = -10;
		dy_g = 0;
    }

    if (keyPressed === UP_KEY && !goingDown) {
		dx_g = 0;
		dy_g = -10;
    }

    if (keyPressed === RIGHT_KEY && !goingLeft) {
		dx_g = 10;
		dy_g = 0;
    }

    if (keyPressed === DOWN_KEY && !goingDown) {
		dx_g = 0;
		dy_g = 10;
    }
}

function randomTen( min, max) {
	return Math.round(( Math.random() * (max-min)+min) / 10)*10;
}

function createFood() {
	foodX = randomTen(0, gameBoard.width - 10);
	foodY = randomTen( 0, gameBoard.height - 10);

	snake.forEach( function isFoodOnSnake(part) {
		const foodIsOnSnake = part.x == foodX && part.y==foodY
		if ( foodIsOnSnake)
			createFood();
	});
}

function didGameEnd() {
	for ( let i = 1; i < snake.length; i++) {
		const didCollide = snake[i].x === snake[0].x &&  snake[i].y === snake[0].y
		if ( didCollide) {
			alert("didCollide() " + i);
			return true;
		}
	}

	const hitLeftWall = snake[0].x < 0;
	const hitRightWall = snake[0].x > gameBoard.width - 10;
	const hitTopWall = snake[0].y < 0;
	const hitBottomWall = snake[0].y > gameBoard.height - 10;

	if( hitLeftWall || hitRightWall || hitTopWall || hitBottomWall) {
		alert("in the Wall");
		return true;
	}
}


function main() {
	if ( didGameEnd())
		return;

	setTimeout( function onTick() {
		changingDirection = false;

		clearBoard();
		drawFood();
		advanceSnake();
		drawSnake();

		main();
	}, 150 )
}

/* Main
 * 
 * 
 */

clearBoard();
drawSnake();

// GLOBAL_VAR
let dx_g=10; let dy_g=0;
let score_g = 0;

createFood();
main();

