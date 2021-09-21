from players.entity import Player
from commands.say import SayFilter
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

@SayFilter
def sayfilter(command, index, teamonly):
	userid = None
	if index:
		userid = Player(index).userid
		if userid and command:
			text = command[0].replace('!', '', 1).replace('/', '', 1).lower()
			if text == 'votemute':
				send_votemenu(userid)
				return False
                
def send_votemenu(userid):
	menu = PagedMenu(title='Votemute\n')
	for player in PlayerIter('human'):
		if not userid == player.userid:
			if not VotedPlayer.from_userid(player.userid).is_voted_mute:
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
		SayText2(f'{RED}[Vote Mute] » {GREEN}{player.name} {LIGHT_GREEN}has voted muted {GREEN}{target.name}').send()
		SayText2(f'{RED}[Vote Mute] » {GREEN}{target.name} {LIGHT_GREEN}has {GREEN}{target.is_votemuted} of {votes} {LIGHT_GREEN}votes to {GREEN}mute').send()
		if target.is_votemuted >= votes:
			target.is_voted_mute = True
			target.mute()
			SayText2(f'{RED}[Vote Mute] » {GREEN}{target.name} {LIGHT_GREEN}has been {GREEN}voted {LIGHT_GREEN}to {GREEN}mute!').send()
