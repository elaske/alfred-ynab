#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan Laske
# @Date:   2014-03-15 15:09:17
# @Last Modified by:   Evan Laske
# @Last Modified time: 2014-03-15 15:13:27

import os.path
import ynabparse
import alp

if __name__ == "__main__":   
    # If we have a setting for the location, use that
    s = alp.Settings()
    path = s.get("budget_path", "")
    if not path == "":
        path = ynabparse.find_budget(path)

    # Else, we guess...
    # First we look in Dropbox
    if path == "":
        path = ynabparse.check_for_budget(os.path.expanduser("~/Dropbox/YNAB"))

    # Then we look locally
    if path == "":
        path = ynabparse.check_for_budget(os.path.expanduser("~/Documents/YNAB"))

    # Then we give up
    if path == "":
        handle_error("Unable to guess budget location", "Use Alfred's File Action on your budget file to configure", "icon-no.png")

    # Load data
    ynabparse.debug_print(path)
    data = ynabparse.load_budget(path)
    ynabparse.get_currency_symbol(data)

    all = ynabparse.all_categories(data)
    query = alp.args()[0]
    results = alp.fuzzy_search(query, all, key = lambda x: '%s' % x["name"])

    items = []

    for r in results:
        # Find category ID matching our requirement
        entityId = r["entityId"]

        if entityId == "":
            pass
        else:
            ending_balance = ynabparse.new_walk_budget(data, entityId)

            if ending_balance == None:
                ending_balance = 0

            if ending_balance < 0:
                ending_text = "Overspent on %s this month!"
                icon = "icon-no.png"
            elif ending_balance == 0:
                ending_text = "No budget left for %s this month"
                icon = "icon-no.png"
            else:
                ending_text = "Remaining balance for %s this month"
                icon = "icon-yes.png"
            try:
                i = alp.Item(title=locale.currency(ending_balance, True, True).decode("latin1"), subtitle = ending_text % r["name"], uid = entityId, valid = False, icon = icon)
            except Exception, e:
                i = alp.Item(title="%0.2f" % ending_balance, subtitle = ending_text % r["name"], uid = entityId, valid = False, icon = icon)
            items.append(i)

    alp.feedback(items)
