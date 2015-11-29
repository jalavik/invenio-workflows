# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Search functions for Holding Pen interface."""

from flask import current_app

from invenio_base.globals import cfg

from invenio_search.api import Query


def search(query, per_page, page, sorting={}):
    """Return a slice of matched workflow object IDs and total hit-count."""
    results = Query(query)
    # Disable enhancing to avoid searching in default collection only
    response = results.search(enhance=False)
    response.index = cfg["WORKFLOWS_HOLDING_PEN_ES_PREFIX"] + "*"
    response.doc_type = current_app.config.get("WORKFLOWS_HOLDING_PEN_DOC_TYPE")
    if sorting:
        response.body.update(sorting)
    response.body["size"] = per_page
    response.body["from"] = (page - 1) * per_page
    current_app.logger.debug(response.body)
    results = response._search()["hits"]
    return [int(r["_id"]) for r in results["hits"]], results["total"]


def get_holdingpen_objects(tags_list=None,
                           sort_key="modified",
                           per_page=25,
                           page=1,
                           operator="AND"):
    """Get records for display in Holding Pen, return ids and total count."""
    if sort_key.endswith("_desc"):
        order = "desc"
        sort_key = sort_key[:-5]
    else:
        order = "asc"

    if not sort_key:
        sort_key = "modified"

    sorting = {
        "sort": {
            sort_key: {
                "order": order
            }
        }
    }
    return search(
        query=" {0} ".format(operator).join(tags_list),
        per_page=per_page,
        page=page,
        sorting=sorting
    )
