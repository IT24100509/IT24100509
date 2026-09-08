
    def get_percept(self) -> dict:
        return {
            'agent_pos': list(self.agent_pos),
            'opponent_positions': [list(op) for op in self.opponents],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions),
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions)
        }
