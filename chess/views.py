from pyramid.view import (
    view_config,
    view_defaults
)
from chess.helpers import query_to_json;
from chess.helpers import get_json_response;
from chess.game.main.game import Game
from pyramid.httpexceptions import HTTPFound
from chess.session.player import Player
from chess.game.enums import ColorEnum
import random

@view_defaults(renderer='home.pt')
class Views:
    def __init__(self, request):
        self.request = request
        self.game = Game()

    @view_config(route_name='board')
    def board(self):
        session = self.request.session
        if 'player' not in session:
            url = self.request.route_url('login')
            return HTTPFound(location=url)

        player = self.game.find_player_by('id', session['player']['id'])
        if player == None:
            url = self.request.route_url('login')
            return HTTPFound(location=url)

        return get_json_response(name='board', title='Game')

    @view_config(route_name='board_data', renderer='json')
    def board_data(self):
        query = self.request.query_string
        data = query_to_json(query)
        board_version = str(self.game.board.version)
        if str(data['version']) != board_version:
            session = self.request.session
            oponent = self.game.find_oposite_player_by('id', session['player']['id'])
            player = self.game.find_player_by('id', session['player']['id'])
            player_color = player.color
            oponent_color = oponent.color
            return {
                'board': self.game.get_board_status(),
                'version': board_version,
                'players': {
                    player_color: player.name,
                    oponent_color: oponent.name
                },
                'color': player_color,
                'check': self.game.is_check_value or self.game.is_checkmate_value,
                'mate': self.game.is_checkmate_value,
                'playersTurn': self.game.is_player_turn(player)
            }
        return {
            'isEmpty': True,
        }

    @view_config(route_name='move', request_method='POST', renderer='json')
    def move(self):
        data = self.request.json_body

        session = self.request.session
        if 'player' not in session:
            url = self.request.route_url('login')
            return HTTPFound(location=url)

        player = self.game.find_player_by('id', session['player']['id'])
        if player == None:
            url = self.request.route_url('login')
            return HTTPFound(location=url)

        self.game.create_move(player.id, data['from']['x'], data['from']['y'], data['to']['x'], data['to']['y'])
        
        return data

    @view_config(route_name='login')
    def login(self):
        session = self.request.session
        if 'player' in session:
            player = self.game.find_player_by('id', session['player']['id'])
            if player != None:
                if len(self.game.players) == 2:
                    url = self.request.route_url('board')
                    return HTTPFound(location=url)
                else:
                    url = self.request.route_url('loading')
                    return HTTPFound(location=url)

        return get_json_response(name='login', title='Login')

    @view_config(route_name='login', request_method='POST')
    def send_login(self):
        json = query_to_json(self.request.text)
        session = self.request.session
        players_len = len(self.game.players)

        if ('username' not in json or json['username'] == ''):
            return get_json_response(name='login', title='Login', error='Please enter your name first')

        if (self.game.find_player_by('name', json['username'])):
            return get_json_response(name='login', title='Login', error='Player with such name is already exists')

        if (players_len == 2):
            return get_json_response(name='login', title='Login', error='Game is already have 2 players')

        if 'player' in session:
            player = self.game.find_player_by('id', session['player']['id'])
            if player == None:
                del session['player']

        if 'player' not in session:
            color = random.choice(list(ColorEnum))
            if players_len == 1:
                color = ColorEnum.WHITE if self.game.players[0].color == ColorEnum.BLACK  else ColorEnum.BLACK
            player = Player(json['username'], color)
            session['player'] = player.__dict__
            self.game.add_player(player)

        url = self.request.route_url('loading')
        return HTTPFound(location=url)

    @view_config(route_name='loading')
    def loading(self):
        session = self.request.session
        if 'player' in session:
            player = self.game.find_player_by('id', session['player']['id'])
            if player != None:
                if len(self.game.players) == 2:
                    url = self.request.route_url('board')
                    return HTTPFound(location=url)
            else:
                url = self.request.route_url('login')
                return HTTPFound(location=url)
        else:
            url = self.request.route_url('login')
            return HTTPFound(location=url)
    
        return get_json_response(name='loading', title='Waiting for another player')

    @view_config(route_name='check_readiness', renderer='json')
    def check_readiness(self):
        if (len(self.game.players) == 2):
            return {
                'isReady': True,
            }

        return {
            'isReady': False,
        }
    
