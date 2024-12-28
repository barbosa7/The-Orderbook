from typing import Dict
import time
from .competition import Competition

class CompetitionManager:
    def __init__(self):
        self.active_competitions: Dict[str, Competition] = {}
        self.create_default_competition()

    def create_default_competition(self):
        competition = Competition(
            competition_id="default_competition",
            name="Default Competition",
            start_time=time.time(),
            end_time=time.time() + 3600
        )
        self.active_competitions["default_competition"] = competition
        return competition

    def add_participant(self, competition_id: str, user_id: str, display_name: str) -> bool:
        competition = self.active_competitions.get(competition_id)
        if not competition:
            competition = self.create_default_competition()
        return competition.add_participant(user_id, display_name)

    def get_leaderboard(self, competition_id: str):
        competition = self.active_competitions.get(competition_id)
        if not competition:
            return []
        
        # Get PnL for each participant and sort by PnL
        participants_pnl = [
            {
                "user_id": user_id,
                "total_pnl": competition.get_participant_pnl(user_id),
            }
            for user_id in competition.participants.keys()
        ]
        
        # Sort by PnL and add rank
        sorted_participants = sorted(participants_pnl, key=lambda x: x["total_pnl"], reverse=True)
        for rank, participant in enumerate(sorted_participants, 1):
            participant["rank"] = rank
        
        return sorted_participants
 