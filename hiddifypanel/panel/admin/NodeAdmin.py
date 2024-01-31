from hiddifypanel.panel.database import db
import copy
from wtforms.validators import Regexp, ValidationError
from flask_babel import lazy_gettext as _
from .adminlte import AdminLTEModelView
from flask_babel import gettext as __
from flask import Markup, g, request

from hiddifypanel.panel.auth import login_required
from hiddifypanel.panel import hiddify
import hiddifypanel.panel.auth as auth
from hiddifypanel.models import *
from hiddifypanel import hutils
from sqlalchemy.orm.session import make_transient


class NodeAdmin(AdminLTEModelView):
    column_hide_backrefs = False
    column_list = ["name", "mode", "unique_id"]
    form_columns = ["name", "mode", "unique_id"]
    column_labels = {
        "name": _("child.name.label"),
        "mode": _("child.mode.label"),
        "unique_id": _("child.uuid.label")
    }
    column_descriptions = {
        "name": _("child.name.dscr"),
        "mode": _("child.mode.dscr"),
        "unique_id": _("child.uuid.dscr")
    }

    def name_formater(view, context, model, name):
        res = hiddify.get_account_panel_link(g.account, request.host, prefere_path_only=True, child_id=model.id)
        return Markup(f"<a href='{res}'>{model.name}</a>")
    column_formatters = {
        'name': name_formater,
    }
    can_export = False

    def is_accessible(self):
        if login_required(roles={Role.super_admin})(lambda: True)() != True:
            return False
        if hutils.current_child_id() != 0:
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        return auth.redirect_to_login()  # type: ignore

    def on_model_change(self, form, model, is_created):
        if is_created and model.mode != ChildMode.virtual:
            raise ValidationError(_("Remote nodes are not supported yet!"))

    def after_model_change(self, form, model, is_created):
        set_hconfig(ConfigEnum.is_parent, True)
        if is_created and model.mode == ChildMode.virtual:
            # for k, v in get_hconfigs().items():
            #     set_hconfig(k, v, model.id)

            items_to_dup = []
            for p in Proxy.query.filter(Proxy.child_id == 0).all():
                p = hiddify.clone_model(p)
                p.child_id = model.id
                items_to_dup.append(p)
            for c in StrConfig.query.filter(StrConfig.child_id == 0).all():
                c = hiddify.clone_model(c)
                c.child_id = model.id
                items_to_dup.append(c)
            for c in BoolConfig.query.filter(BoolConfig.child_id == 0).all():
                c = hiddify.clone_model(c)
                c.child_id = model.id
                items_to_dup.append(c)
            d = Domain()
            d.alias = f'{model.name}-def'
            d.domain = f"{model.id}.{hutils.network.get_ip_str(4)}.sslip.io"
            d.child_id = model.id
            items_to_dup.append(d)

            db.session.bulk_save_objects(items_to_dup)
            db.session.commit()
            set_hconfig(ConfigEnum.is_parent, False, model.id)
            set_hconfig(ConfigEnum.parent_panel, hiddify.get_account_panel_link(g.account, request.host), model.id)