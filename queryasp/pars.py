# def pa(s,loc,toks):
#     print("**DEBUG:In pa: s={0!r} loc={1!r} toks={2!r}".format(s, loc, toks))

# rpar=Literal("]")
# lpar=Literal("[")
# legalbechar = prs.Regex(r"[^\[\]\s]")
# legalchar = prs.Regex(r"[^\[\]]")
# legalchar = prs.srange("a-zA-Z0-9")
# innercontent = r"([^&\|])"
# atom = prs.Regex(r"-?[a-z_][a-zA-Z0-9_]*(\(" + innercontent + r"+\))?")
# atom = Word(legalcontchars) + (prs.White() + Word(legalcontchars))*(0,None)


# optcneg = prs.Optional((prs.Suppress("-")))
# legalcontchars= prs.printables.replace("[",'').replace("]",'')
# #operand = optcneg + prs.Word(alphanums+"_") + prs.Suppress("(") + prs.Suppress(")")
# term_name =  prs.Word(prs.alphas)
# op_kw =  prs.Literal(" not ") | prs.Literal(" & ") | prs.Literal(" | ")
# #term_body = prs.nestedExpr(opener='(', closer=')', content=term_name)
# content= Word(legalcontchars) + ~prs.FollowedBy(prs.WordEnd())
# term_body=  prs.Literal("(")+ content + prs.Literal(")") + prs.FollowedBy(prs.White())
# operand = optcneg + term_name + term_body
# operand.setParseAction(pa)


#atom = prs.Regex(r"-?[^\[\](),]+(\(.+\))?")
# parcontent = prs.OneOrMore(prs.Word(prs.printables) | prs.White())
# parbody = prs.nestedExpr( '(', ')', content=parcontent)
# atom_name = (prs.Word(legalchar) + prs.Optional(prs.White()))*(1,None)
# atom = atom_name 
#atom = prs.Combine(Word(prs.alphas) + prs.Optional( prs.Group(prs.Suppress("(") + (Word(prs.alphas)| prs.White())  + prs.Suppress("(")) ))

#operand = prs.OneOrMore(Word(prs.printables) + prs.Optional(prs.White(' ')) )
#operand = atom
#char = prs.Regex("\w(\s\w)*")
#operand = ~Literal("[") + prs.Regex(r"\w(\s\w_)*") + ~Literal("]")
#operand =  prs.Combine(legalbechar + legalchar*(0,100) + legalbechar)



# sameLevelExpr = nestedExpr(opener='[', closer=']')
# connectivesExpr = oneOf ("&|")
# queryExpr =  sameLevelExpr + ZeroOrMore( connectivesExpr + sameLevelExpr)
# print(queryExpr.parseString(query))

# QUERY = Group(LPAREN + ZeroOrMore(LITERAL + OneOrMore(OP + LITERAL)) + LPAREN)

# LPAREN = prs.Literal("[")
# RPAREN = prs.Literal("]")
# OR = prs.Literal("|")
# AND = prs.Literal("&")
# OP = AND | OR
# LITERAL = prs.ch
# QUERY = prs.Group(LPAREN + LITERAL + RPAREN)
# queryExpr = prs.Forward()
# queryExpr << QUERY

# query = '[[not a(foo)|b]b(cd,df)&b]'
#query="[a]"
# print("\n"+query)
#print(queryExpr.parseString(query))
