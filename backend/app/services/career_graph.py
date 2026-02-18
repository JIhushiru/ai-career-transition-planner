"""Career graph traversal and pathfinding service."""

import heapq
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_graph import CareerTransition
from app.models.role import Role


class CareerGraphService:
    async def get_adjacency(self, db: AsyncSession) -> dict[int, list[dict]]:
        """Build adjacency list from career_transitions table."""
        result = await db.execute(select(CareerTransition))
        transitions = result.scalars().all()

        adj: dict[int, list[dict]] = {}
        for t in transitions:
            if t.from_role_id not in adj:
                adj[t.from_role_id] = []
            adj[t.from_role_id].append({
                "to_role_id": t.to_role_id,
                "difficulty": t.difficulty,
                "months": t.typical_months or 12,
                "viability": t.market_viability,
                "upskills": json.loads(t.required_upskills) if t.required_upskills else [],
                "type": t.transition_type,
            })
        return adj

    async def find_paths(
        self,
        db: AsyncSession,
        start_role_id: int,
        target_role_id: int,
        max_steps: int = 4,
        max_paths: int = 5,
    ) -> list[list[dict]]:
        """Find career transition paths using modified Dijkstra's algorithm.

        Returns up to max_paths shortest paths from start to target role,
        each path being a list of transition steps.
        """
        adj = await self.get_adjacency(db)
        paths: list[list[dict]] = []

        # Priority queue: (cost, current_role_id, path_so_far)
        pq: list[tuple[float, int, list[dict]]] = [(0.0, start_role_id, [])]
        visited_counts: dict[int, int] = {}

        while pq and len(paths) < max_paths:
            cost, current, path = heapq.heappop(pq)

            if len(path) > max_steps:
                continue

            visit_count = visited_counts.get(current, 0)
            if visit_count >= max_paths:
                continue
            visited_counts[current] = visit_count + 1

            if current == target_role_id and path:
                paths.append(path)
                continue

            for edge in adj.get(current, []):
                edge_cost = edge["difficulty"] * (1 - edge["viability"] * 0.3)
                new_cost = cost + edge_cost
                new_path = path + [{
                    "from_role_id": current,
                    "to_role_id": edge["to_role_id"],
                    "difficulty": edge["difficulty"],
                    "months": edge["months"],
                    "upskills": edge["upskills"],
                    "type": edge["type"],
                }]
                heapq.heappush(pq, (new_cost, edge["to_role_id"], new_path))

        return paths

    async def find_reachable_roles(
        self,
        db: AsyncSession,
        start_role_id: int,
        max_steps: int = 2,
    ) -> list[dict]:
        """Find all roles reachable within max_steps transitions."""
        adj = await self.get_adjacency(db)
        reachable: dict[int, dict] = {}

        queue: list[tuple[int, int, float, int]] = [(start_role_id, 0, 0.0, 0)]
        visited: set[tuple[int, int]] = set()

        while queue:
            current, steps, total_diff, total_months = queue.pop(0)

            if steps > max_steps:
                continue

            state = (current, steps)
            if state in visited:
                continue
            visited.add(state)

            if current != start_role_id:
                if current not in reachable or reachable[current]["steps"] > steps:
                    reachable[current] = {
                        "role_id": current,
                        "steps": steps,
                        "total_difficulty": round(total_diff, 3),
                        "total_months": total_months,
                    }

            for edge in adj.get(current, []):
                queue.append((
                    edge["to_role_id"],
                    steps + 1,
                    total_diff + edge["difficulty"],
                    total_months + edge["months"],
                ))

        return sorted(reachable.values(), key=lambda x: x["total_difficulty"])

    async def get_role_map(self, db: AsyncSession) -> dict[int, Role]:
        """Get mapping of role_id -> Role for all roles."""
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        return {r.id: r for r in roles}
