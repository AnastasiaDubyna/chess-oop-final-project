(function main () {
    const state = {
        version: -1
    };

    function comparePositions(a, b) {
        return a.x === b.x && a.y === b.y
    }

    function createPosition(x, y) {
        return { y: x, x: 8 - y - 1 };
    }

    function fetchBoardData() {
        return fetch(`/board-data?version=${state.version}`)
        .then(response => response.json());
    }

    function makeMove(data) {
        return fetch('/move', {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
              'Content-Type': 'application/json'
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: JSON.stringify(data)
          }).then(response => response.json());
    };

    function selectPiece(x, y, target) {
        $target = $(target);
        if (
            !state.playersTurn ||
            (!$target.hasClass('board-piece-white')
            && !$target.hasClass('board-piece-black'))
            || ($target.hasClass('board-piece-white') && state.color === 'black')
            || ($target.hasClass('board-piece-black') && state.color === 'white')
        ) {
            return;
        }
        $target.addClass('selected');

        state.selected = { 
            position: createPosition(x, y),
            $target
         };
    }

    function unselectPiece() {
        state.selected.$target.removeClass('selected');
        state.selected = null;
    }

    function generateLettersRow () {
        let $row = $('<div/>', { class: 'letters-row' });
        const letters = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', ''];
        letters.forEach((letter) => {
            $row.append(
                $('<div/>', {
                    class: `letters-cell`,
                    text: letter
                })
            );
        });
        return $row;
    }

    function generateRowNumberCell (number) {
        return $('<div/>', {
            class: `row-number-cell`,
            text: number
        });
    }

    function renderBoard(items) {
        const $container = $('.main-container');
        const $board = $('<div/>', { class: 'board' });
        const $blackPlayer = $('<div/>', { class: 'black-player' });
        const $whitePlayer = $('<div/>', { class: 'white-player' });
        $container.empty();
        $board.append(generateLettersRow());
        items.forEach((row, yIndex) => {
            let $row = $('<div/>', { class: 'board-row' });
            $row.append(generateRowNumberCell(yIndex + 1));
            row.forEach((cell, xIndex) => {
                const pieceClass = cell.color ? `board-piece-${cell.color}` : ''
                const styles = cell.color !== state.color ? { cursor: 'default' } : {};
                $row.append(
                    $('<div/>', {
                        class: `board-cell ${pieceClass}`,
                        text: cell.piece,
                        css: styles,
                        on: {
                            click: (event) => {
                                if (state.selected && comparePositions(state.selected.position, createPosition(xIndex, yIndex))) {
                                    unselectPiece();
                                    return;
                                }
                                if (state.selected) {
                                    makeMove({
                                        from: state.selected.position,
                                        to:  createPosition(xIndex, yIndex)
                                    })
                                    .then(() => {
                                        boardPolling();
                                    })
                                    .finally(() => {
                                        unselectPiece();
                                    });
                                } else {
                                    selectPiece(xIndex, yIndex, event.target);
                                }
                            }
                        }
                    })
                );
            });
            $row.append(generateRowNumberCell(yIndex + 1));
            $board.append($row);
        });
        $board.append(generateLettersRow());
        $container.append($blackPlayer);
        $container.append($board);
        $container.append($whitePlayer);
    }

    function updateBoard() {
        fetchBoardData()
            .then(data => {
                if (data && !data.isEmpty) {
                    state.version = data.version;
                    state.color = data.color;
                    state.playersTurn = data.playersTurn;
                    renderBoard(data.board);
                    $('.black-player').text(data.players.black);
                    $('.white-player').text(data.players.white);
                    if (state.playersTurn) {
                        $(`.${state.color}-player`).append('<div>Your turn</div>');
                    }
                    if (data.check && data.mate) {
                        alert('Check and mate');
                    } else if (data.check) {
                        alert('Check');
                    }
                }
            });
    }


    function boardPolling() {
        if (state.pollingId) {
            clearInterval(state.pollingId);
        }
        updateBoard();
        state.pollingId = setInterval(() => {
            updateBoard();
        }, 3000);
    }

    boardPolling();

})();
