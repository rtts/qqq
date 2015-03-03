from django import template

register = template.Library()

@register.filter
def multiplyby(value, arg):
  return int(value * arg)

@register.filter
def subtractfrom(value, arg):
  return arg - value

@register.filter
def plus(value, arg):
  return value + arg

@register.filter
def appears_in(value, arg):
  for name in arg:
    if name == value: return True
  return False

@register.filter
def length(value):
  return len(value)

@register.filter
def user_can_downvote(votes, id):
  if id not in votes: return True
  if votes[id].is_downvote(): return False
  return True

@register.filter
def user_can_upvote(votes, id):
  if id not in votes: return True
  if votes[id].is_upvote(): return False
  return True

@register.filter
def stripnewlines(str):
  return str.replace('\n', ' ').replace('\r', ' ')
