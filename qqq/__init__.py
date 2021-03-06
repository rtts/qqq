from django.utils.encoding import smart_unicode

# translation mapping table that converts
# single smart quote characters to standard
# single quotes
SINGLE_QUOTE_MAP = {
	0x2018: 39, 
	0x2019: 39,
	0x201A: 39,
	0x201B: 39,
	0x2039: 39,
	0x203A: 39,
}

# translation mapping table that converts
# double smart quote characters to standard
# double quotes
DOUBLE_QUOTE_MAP = {
	0x00AB: 34,
	0x00BB: 34,
	0x201C: 34,
	0x201D: 34,
	0x201E: 34,
	0x201F: 34,
}

def convert_smart_quotes(str):
	"""
	Convert "smart quotes" from Microsoft products
	to standard quotes.
	"""
	return smart_unicode(str).translate(DOUBLE_QUOTE_MAP).translate(SINGLE_QUOTE_MAP)
