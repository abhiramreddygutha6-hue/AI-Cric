"""SQL building blocks mirroring the rules in services/stats.py (so database totals and
row-by-row stats agree)."""
from sqlalchemy import and_, case, extract, or_
from app.models import Delivery, Match, Tournament
from app.services.stats import BOWLER_WICKET_KINDS, CHARGED_EXTRAS, NOT_A_DISMISSAL

CHARGED = sorted(CHARGED_EXTRAS)
LEGAL = or_(Delivery.extra_type.is_(None), Delivery.extra_type.notin_(CHARGED))
NOT_WIDE = or_(Delivery.extra_type.is_(None), Delivery.extra_type != "wides")

# bowler side
legal_n = case((LEGAL, 1), else_=0)
charged_runs = Delivery.runs_batter + case((Delivery.extra_type.in_(CHARGED), Delivery.runs_extras), else_=0)
bowler_wicket = case((and_(Delivery.is_wicket.is_(True),
                           Delivery.wicket_kind.in_(sorted(BOWLER_WICKET_KINDS))), 1), else_=0)
legal_dot_charged = case((and_(LEGAL, charged_runs == 0), 1), else_=0)
legal_boundary = case((and_(LEGAL, Delivery.runs_batter.in_((4, 6))), 1), else_=0)

# batter side
faced_n = case((NOT_WIDE, 1), else_=0)
faced_dot = case((and_(NOT_WIDE, Delivery.runs_batter == 0), 1), else_=0)
faced_four = case((and_(NOT_WIDE, Delivery.runs_batter == 4), 1), else_=0)
faced_six = case((and_(NOT_WIDE, Delivery.runs_batter == 6), 1), else_=0)
dismissal = case((and_(Delivery.is_wicket.is_(True),
                       Delivery.wicket_kind.notin_(sorted(NOT_A_DISMISSAL))), 1), else_=0)


def scope(stmt, phase=None, tournament=None, season=None):
    """Join matches and apply the optional phase / tournament / season filters."""
    stmt = stmt.select_from(Delivery).join(Match, Match.id == Delivery.match_id)
    if phase:
        stmt = stmt.where(Delivery.phase == phase)
    if tournament:
        stmt = stmt.join(Tournament, Tournament.id == Match.tournament_id) \
                   .where(Tournament.name.ilike(f"%{tournament}%"))
    if season:
        stmt = stmt.where(extract("year", Match.match_date) == season)
    return stmt
