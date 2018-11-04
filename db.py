import dataset

class DB(object):
  def __init__(self):
    super(DB, self).__init__()
    self.db = dataset.connect('sqlite:///:memory:')
    self.db.create_table('lights', primary_id='light_id')

  def clear_lights():
    self.db.delete(type='light')

  def get_lights(self):
    table = self.db['lights']
    return table.find(type='light')

  def add_light(self, light_id, name, bri, hue, on):
    table = self.db['lights']
    data = dict(light_id=light_id, brightness=bri, hue=hue, on=on, type='light', name=name)
    table.insert(data)
