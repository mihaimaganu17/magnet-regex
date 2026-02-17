# Regex grammar
In order of precedence, lowest to highest:

alteration := concat('|' concat)*
concat := quantified*
quantified := atom quantifier?
atom := char | charclass | group | anchor | lookaround | '.'
quantifier := '*'|'+'|'?'| '{' number (',' number?)? '}'