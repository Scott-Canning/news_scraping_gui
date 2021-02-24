class Search_Term:
    def __init__(self, tag, term):
        self.tag = tag
        self.term = term

# list of Search_Term objects
search_list = []

pltr = Search_Term('$PLTR', 'Palantir')
dkng = Search_Term('$DKNG', 'DraftKings')
sq = Search_Term('$SQ', 'Square')
shop = Search_Term('$SHOP', 'Shopify')
docu = Search_Term('$DOCU', 'DocuSign')

search_list.append(pltr)
search_list.append(dkng)
search_list.append(sq)
search_list.append(shop)
search_list.append(docu)
