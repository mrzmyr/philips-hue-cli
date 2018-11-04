from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from phue import Bridge, PhueRegistrationException
import os
from db import DB

db = DB()
b = None

def get_action():
  return prompt([{
    'type': 'list',
    'name': 'action',
    'message': 'What do you want to do?',
    'choices': [{
      'name': 'Connect to Bridge',
      'value': 'connect'
    }, {
      'name': 'Change Light',
      'value': 'lights_change'
    }, {
      'name': 'Show Lights in Database',
      'value': 'db_lights_show'
    }, {
      'name': 'Save Lights in Database',
      'value': 'db_lights_save'
    }, {
      'name': 'Restore Lights from Database',
      'value': 'db_lights_restore'
    }, {
      'name': 'Clear Cache (saved IP)',
      'value': 'cache_clear'
    }]
  }])['action']

def get_light_action():
  return prompt([{
    'type': 'list',
    'name': 'action',
    'message': 'What do you want to do?',
    'choices': [{
      'name': '× done',
      'value': 'done'
    }, {
      'name': 'Turn off / on',
      'value': 'light_switch'
    }, {
      'name': 'Change hue',
      'value': 'light_hue'
    }, {
      'name': 'Change brightness',
      'value': 'light_brightness'
    }]
  }])['action']

def connect(ip):
  try:
    global b
    b = Bridge(ip)
    b.connect()
    b.connected = True
    return { 'ok': True, 'message': 'Connected to %s!' % b.username, 'brigde': b }
  except Exception as e:
    return { 'ok': False, 'message': e.message, 'brigde': None }

def cache_clear():
  global b
  b = None
  os.remove("./ip.txt")

def save_ip(ip):
  with open('./ip.txt', 'w') as f:
    f.write(ip)

def get_ip():
  try:
    with open('./ip.txt') as f:
      return f.read()
  except FileNotFoundError as e:
    return None

def ask_for_ip():
  return prompt([{
    'type': 'input',
    'name': 'ip',
    'message': 'What\'s the IP of your brigde ?',
    'default': '192.168.0.232'
  }])['ip']

def select_hue():
  answers = prompt([{
    'type': 'input',
    'name': 'hue',
    'message': 'At what hue do you want your light? (0 - 360)',
    'default': '120'
  }])

  return int(answers['hue'])

def select_brightness():
  answers = prompt([{
    'type': 'input',
    'name': 'brightness',
    'message': 'At what brightness do you want your light? (0 - 254)',
    'default': '50'
  }])

  return int(answers['brightness'])

def select_light(lights):
  choices = [{
    'name': '× done',
    'value': 'done'
  }]

  for l in lights:
    choices.append({
      'name': l.name,
      'value': str(l.light_id)
    })

  answers = prompt([{
    'type': 'list',
    'name': 'light_id',
    'message': 'Which light do you want to change?',
    'choices': choices
  }])

  if answers['light_id'] is not 'done':
    return int(answers['light_id'])
  else:
    return 'done'

def is_connected():
  if b is None or not b.connected:
    return False

if __name__ == "__main__":

  print()

  ip = get_ip()
  if ip is not None:
    print('Found IP in Cache:', ip)
    connection = connect(ip)
    print(connection['message'])
    print()

  while(True):
    print()

    action = get_action()

    if action is 'connect':
      ip = ask_for_ip()
      connection = connect(ip)
      if connection['ok']:
        save_ip(ip)
      print()
      print(connection['message'])

    if action is 'lights_change':
      while(True):
        selected_light_id = select_light(b.lights)

        if selected_light_id is 'done':
          break

        while(True):
          light_action = get_light_action()

          if light_action == 'done':
            break

          if light_action == 'light_switch':
            is_on = b.get_light(selected_light_id, 'on')
            b.set_light(selected_light_id, 'on', not is_on)

          if light_action == 'light_hue':
            hue = select_hue()
            b.set_light(selected_light_id, 'hue', hue)

          if light_action == 'light_brightness':
            bri = select_brightness()
            b.set_light(selected_light_id, 'bri', bri)

    if action is 'db_lights_show':
      for l in db.get_lights():
        print(l)

    if action is 'db_lights_save':
      for l in b.lights:
        db.add_light(l.light_id, l.name, l.brightness, l.hue, l.on)

    if action is 'db_lights_restore':
      for l in db.get_lights():
        b.set_light(l['light_id'], 'bri', l['brightness'])
        b.set_light(l['light_id'], 'hue', l['hue'])
        b.set_light(l['light_id'], 'on', l['on'])

    if action is 'cache_clear':
      cache_clear()
