import socket
import json
import os

from rlgym_sim.utils.gamestates import GameState

UDP_IP = "127.0.0.1"
UDP_PORT = 9273 # Default RocketSimVis port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

_designated_renderer_pid = None

def write_physobj(physobj):
	j = {}
	
	j['pos'] = physobj.position.tolist()
	j['forward'] = physobj.forward().tolist()
	j['up'] = physobj.up().tolist()
	j['vel'] = physobj.linear_velocity.tolist()
	j['ang_vel'] = physobj.angular_velocity.tolist()
	
	return j

def write_car(player):
	j = {}
	
	j['team_num'] = int(player.team_num)
	j['phys'] = write_physobj(player.car_data)
	
	j['boost_amount'] = player.boost_amount * 100
	j['on_ground'] = bool(player.on_ground)
	j['is_demoed'] = bool(player.is_demoed)
	j['has_flip'] = bool(player.has_flip)

	return j

def send_state_to_rocketsimvis(gs: GameState, custom_ui_text: str = None):
	global _designated_renderer_pid

	if _designated_renderer_pid is None:
		_designated_renderer_pid = os.getpid()

	if _designated_renderer_pid != os.getpid():
		return

	j = {}

	# Send ball
	j['ball_phys'] = write_physobj(gs.ball)

	# Send cars
	j['cars'] = []
	for player in gs.players:
		j['cars'].append(write_car(player))

	# Send boost pad states
	j['boost_pad_states'] = gs.boost_pads.tolist()

	# --- ADD BOOST LEVEL TO UI ---
	if custom_ui_text is not None:
		j['ui_text'] = custom_ui_text
	else:
	# Auto-generate a clean boost UI display for all players on the field
		boost_entries = []
		for i, player in enumerate(gs.players):
			team_name = "BLUE" if player.team_num == 0 else "ORANGE"
			boost_pct = int(player.boost_amount * 100)
			boost_entries.append(f"{team_name} Car:{boost_pct}% Boost")
				
		# Join them with a separator
		j['ui_text'] = " | ".join(boost_entries)
			# -----------------------------
	
	sock.sendto(json.dumps(j).encode('utf-8'),(UDP_IP, UDP_PORT))