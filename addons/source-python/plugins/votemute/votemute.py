from events import Event
from players.entity import Player
from commands.say import SayCommand
from menus import PagedMenu, PagedOption
from players.helpers import index_from_userid
from messages import SayText2
from colors import GREEN, RED, LIGHT_GREEN
from filters.players import PlayerIter

def required_votes():
	return len(PlayerIter(['human', 'all']))

players_required = 2

class VotePlayer(Player):
	caching = True # Uses caching

	def __init__(self, index):
		super().__init__(index)
		self.is_votemuted 	 = 0
		self.is_voted_mute	 = False

@Event('player_disconnect')
def player_disconnect(args):
	player = VotePlayer.from_userid(args['userid'])
	if player.is_voted_mute:
		player.unmute()

for i in ['votemute', '!votemute', '/votemute']:
	@SayCommand(f'{i}')
	def say_command(command, index, teamonly):
		player = Player(index)
		userid = player.userid
		if required_votes() > 1:
			send_votemenu(userid)
			return False
		else:
			SayText2(f"{RED}[Vote Mute] » {GREEN}Server {LIGHT_GREEN}doesn't have enough {GREEN}players, required {LIGHT_GREEN}amount is {GREEN}2").send(player.index)        
			return False

def send_votemenu(userid):
	menu = PagedMenu(title='Votemute\n')
	for player in PlayerIter('human'):
		if not userid == player.userid:
			if not VotePlayer.from_userid(player.userid).is_voted_mute:
				menu.append(PagedOption('%s' % (player.name), (player.userid)))
	menu.select_callback = vote_menu_callback
	menu.send(index_from_userid(userid))
    
def vote_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		votes = int(required_votes() / players_required)
		player = Player(_index)
		target = VotePlayer.from_userid(choice)
		target.is_votemuted += 1
		SayText2(f'{RED}[Vote Mute] » {GREEN}{player.name} {LIGHT_GREEN}has voted mute {GREEN}{target.name}').send()
		SayText2(f'{RED}[Vote Mute] » {GREEN}{target.name} {LIGHT_GREEN}has {GREEN}{target.is_votemuted} of {votes} {LIGHT_GREEN}votes to {GREEN}mute').send()
		if target.is_votemuted >= votes:
			target.is_voted_mute = True
			target.mute()
			SayText2(f'{RED}[Vote Mute] » {GREEN}{target.name} {LIGHT_GREEN}has been {GREEN}voted {LIGHT_GREEN}to {GREEN}mute!').send()
