from django import template
from debate.models import Reply
from debate.forms import ReplyForm
from django.contrib.contenttypes.models import ContentType
from mptt.utils import tree_item_iterator

register = template.Library()

@register.inclusion_tag('debate.html')
def render_debate(object, user):
  """
  This template tag renders a list of threaded replies to a given object.
  The first time this is called for an object, it creates and saves the
  root reply node (but if you do it yourself you can set the notify_user
  attribute).
  
  Currently, the root reply node for qqq.Question and qqq.Post objects
  is created as they're created, and their user is made the user of the
  root reply node.
  
  Don't you just love the level of separation that Django apps provide?
  """
  type = ContentType.objects.get_for_model(object)
  replies = Reply.tree.filter(content_type=type, object_id=object.pk)
  
  if not replies:
    root_reply = Reply(object=object, notify_user=False)
    root_reply.save()
    replies = [root_reply]
  
  list = []
  root_node = None
  for node, meta in tree_item_iterator(replies):
    if not root_node:
      root_node = node
      continue
    if meta['new_level']:
      list.append(+1)
    list.append(node)
    for x in meta['closed_levels']:
      list.append(-1)
  if list:
    list.pop()
  
  return {'ruid': user.id,
          'root': root_node,
          'list': list,
          'object': object}

#  return {'list':
#           [+1,
#             'goeie vraag zeg',
#              +1,
#                'zeg dat wel',
#              -1,
#              'yes ik heb de tweede comment gepost',
#              'en ik de derde',
#            -1],
#          'type': type.name}
