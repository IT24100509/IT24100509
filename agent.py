
import random
from collections import deque
import heapq
import math
from logic_engine import KnowledgeBase


class SimpleReflexAgent:
    """A simple reflex agent using pure condition-action rules without memory."""
    
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here', False):
            return 'Up'
        elif percept.get('wall_ahead', False):
            return 'Left'
        return 'Right'


class ModelBasedAgent:
    """A model-based agent that maintains internal state/memory to avoid infinite loops."""
    
    def __init__(self):
        self.visited_cells = set()
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('wall_ahead', False):
            action = 'Right' if self.last_action == 'Left' else 'Left'
        else:
            action = 'Up'
        
        self.last_action = action
        return action


class SearchAgent:
    """A goal-based search agent implementing A* pathfinding integrated with a Knowledge Base."""
    
    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'
        self.kb = KnowledgeBase()
        
        # Define logical rules in the Knowledge Base
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def astar_search(self, start_pos, goal_pos, walls, grid_size, current_percepts, heuristic_type='manhattan'):
        h_fn = self.manhattan_distance if heuristic_type == 'manhattan' else self.euclidean_distance
        g_cost = 0
        h_cost = h_fn(start_pos, goal_pos)
        f_cost = g_cost + h_cost
        
        frontier = [(f_cost, g_cost, start_pos, [])]
        reached_states = set()
        
        while frontier:
            f, g, current_pos, path = heapq.heappop(frontier)
            
            if tuple(current_pos) == tuple(goal_pos):
                return path
            
            if tuple(current_pos) in reached_states:
                continue
            reached_states.add(tuple(current_pos))
            
            x, y = current_pos
            for action, (nx, ny) in [('Up', (x, y + 1)), ('Down', (x, y - 1)), ('Left', (x - 1, y)), ('Right', (x + 1, y))]:
                if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
                    if (nx, ny) not in walls and (nx, ny) not in reached_states:
                        
                        # Feasibility check via Knowledge Base and Forward Chaining
                        self.kb.clear_facts()
                        # Feed current tile/percept facts to KB
                        if current_percepts.get('smells_food', False):
                            self.kb.tell_fact('TargetVisible')
                            self.kb.tell_fact('HasDust')
                        self.kb.forward_chain()
                        
                        # If 'Retreat' is deduced, the node is infeasible; skip it
                        if 'Retreat' in self.kb.facts:
                            continue
                        
                        new_g = g + 1
                        new_h = h_fn((nx, ny), goal_pos)
                        new_f = new_g + new_h
                        heapq.heappush(frontier, (new_f, new_g, (nx, ny), path + [action]))
        return None

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            agent_pos = percept.get('agent_pos')
            all_food = percept.get('all_food', [])
            grid_size = percept.get('grid_size', (10, 10))
            walls = set(tuple(w) for w in percept.get('walls', []))
            
            if all_food:
                goal_pos = min(all_food, key=lambda f: self.manhattan_distance(agent_pos, f))
                
                if self.active_algo == 'AStar':
                    self.plan = self.astar_search(agent_pos, goal_pos, walls, grid_size, percept, heuristic_type='manhattan')
                
                if not self.plan:
                    return 'Stay'
        
        if self.plan:
            return self.plan.pop(0)
        return 'Stay'
