grammar SCode;

text_adventure
	:	(room break)+
	;
	
room	
	: 	NEW_ROOM CHARS EOL room_desc
	;
	
link
	:	(OPEN_LINK CHARS (ALT_TEXT CHARS)? CLOSE_LINK)
	;
 
room_desc
	:	(room_desc_line ((EOL|break) room_desc_line)*)
	;
	
room_desc_line
	:	(link | CHARS | special | script)+
	;
	
special
	:	NEW_SPECIAL room_desc_line EOL
	;

script
	:	SCRIPT
	;
	
break	:	EOL
	;
	
OPEN_LINK
	:	'[['
	;
    
CLOSE_LINK
	:	']]'
	;
	
EOL
	:	('\n'|'\r'|'\r\n')
	;
    
NEW_ROOM 
	:	'#'
	;
    	
NEW_SPECIAL
	:	'{?' (' '..'|')* '}'
	;
	
SCRIPT
	:	'{' (' '..'|')* '}'
	;
	
ALT_TEXT
	:	'|'
	;
	
CHARS
	:	('a'..'z'|'A'..'Z'|'0'..'9'|'+'|'.'|','|'!'|'-'|'$'|'%'|'^'|'&'|'*'|';'|'\\'|'/'|'<'|'>'|'"'|'\''|':'|'?'|'='|' ')+
	;
	
UNMATCHED
	:	'{'|'}'
	;