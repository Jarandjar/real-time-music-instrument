#!/usr/bin/env python3
"""
Campaign Coordinator - Long-Running Mission Manager

Manages multi-day/week campaigns that spawn hundreds of tasks.
Each campaign has phases, and agents coordinate to achieve long-term goals.

Campaigns:
- CODEBASE_OVERHAUL: Refactor + document repos over weeks
- KNOWLEDGE_ARCHIVE: Build personal knowledge graph
- WORLD_BIBLE: Maintain game/IP lore consistency
- FITNESS_ARC: Multi-month training narrative
"""

import duckdb
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import json
from agent_sdk import log_event


class CampaignPhase:
    """Campaign execution phases"""
    MAPPING = "mapping"           # Understand structure
    ANALYSIS = "analysis"         # Find problems/patterns
    PROPOSAL = "proposal"         # Generate solutions
    EXECUTION = "execution"       # Apply changes
    MONITORING = "monitoring"     # Track impact


class CampaignStatus:
    """Campaign states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class CampaignCoordinator:
    """Manages long-running campaigns"""
    
    def __init__(self, db_path: str = 'evidence.duckdb'):
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        """Initialize campaign tables"""
        conn = duckdb.connect(self.db_path)
        
        # Campaigns table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                campaign_id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                status VARCHAR DEFAULT 'active',
                goal TEXT,
                current_phase VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                meta JSON
            )
        """)
        
        # Campaign tasks linkage
        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaign_tasks (
                campaign_id VARCHAR NOT NULL,
                task_id INTEGER,
                phase VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (campaign_id, task_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
            )
        """)
        
        # Code analysis tables for CODEBASE_OVERHAUL
        conn.execute("""
            CREATE TABLE IF NOT EXISTS code_files (
                file_id VARCHAR PRIMARY KEY,
                campaign_id VARCHAR,
                file_path VARCHAR NOT NULL,
                file_type VARCHAR,
                lines_of_code INTEGER,
                complexity_score FLOAT,
                last_modified TIMESTAMP,
                metadata JSON
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS code_todos (
                todo_id INTEGER PRIMARY KEY,
                file_id VARCHAR,
                line_number INTEGER,
                todo_type VARCHAR,  -- TODO, FIXME, HACK, NOTE, XXX
                content TEXT,
                priority INTEGER DEFAULT 5,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS code_hotspots (
                hotspot_id INTEGER PRIMARY KEY,
                campaign_id VARCHAR,
                file_id VARCHAR,
                hotspot_type VARCHAR,  -- complexity, churn, bug_density
                severity VARCHAR,      -- low, medium, high, critical
                score FLOAT,
                details JSON,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS refactor_proposals (
                proposal_id INTEGER PRIMARY KEY,
                campaign_id VARCHAR,
                file_id VARCHAR,
                proposal_type VARCHAR,  -- split, rename, extract, simplify
                status VARCHAR DEFAULT 'proposed',
                description TEXT,
                estimated_effort VARCHAR,  -- small, medium, large
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        conn.close()
        print("✅ Campaign schema initialized")
    
    def create_campaign(self, campaign_id: str, name: str, goal: str, 
                       campaign_type: str, meta: Dict = None) -> str:
        """Create a new campaign"""
        conn = duckdb.connect(self.db_path)
        
        meta_json = json.dumps(meta or {'type': campaign_type})
        
        conn.execute("""
            INSERT INTO campaigns (campaign_id, name, status, goal, current_phase, meta)
            VALUES (?, ?, 'active', ?, 'mapping', ?)
        """, [campaign_id, name, goal, meta_json])
        
        conn.close()
        
        # Log to event spine
        log_event(
            event_type='campaign_created',
            agent_id='campaign_coordinator',
            realm='campaigns',
            metadata={
                'campaign_id': campaign_id,
                'name': name,
                'type': campaign_type
            },
            content=f"Campaign '{name}' initiated: {goal}"
        )
        
        print(f"📜 Campaign created: {campaign_id}")
        print(f"   Goal: {goal}")
        
        return campaign_id
    
    def get_active_campaigns(self) -> List[Dict]:
        """Get all active campaigns"""
        conn = duckdb.connect(self.db_path)
        
        campaigns = conn.execute("""
            SELECT campaign_id, name, goal, current_phase, created_at, meta
            FROM campaigns
            WHERE status = 'active'
            ORDER BY created_at DESC
        """).fetchall()
        
        conn.close()
        
        return [
            {
                'campaign_id': c[0],
                'name': c[1],
                'goal': c[2],
                'current_phase': c[3],
                'created_at': c[4],
                'meta': json.loads(c[5]) if c[5] else {}
            }
            for c in campaigns
        ]
    
    def generate_phase_tasks(self, campaign_id: str, phase: str) -> List[Dict]:
        """Generate tasks for a specific campaign phase"""
        conn = duckdb.connect(self.db_path)
        
        # Get campaign metadata
        campaign = conn.execute("""
            SELECT name, goal, meta
            FROM campaigns
            WHERE campaign_id = ?
        """, [campaign_id]).fetchone()
        
        if not campaign:
            conn.close()
            return []
        
        name, goal, meta_json = campaign
        meta = json.loads(meta_json) if meta_json else {}
        campaign_type = meta.get('type', 'unknown')
        
        tasks = []
        
        if campaign_type == 'CODEBASE_OVERHAUL':
            tasks = self._generate_codebase_tasks(campaign_id, phase, meta)
        elif campaign_type == 'KNOWLEDGE_ARCHIVE':
            tasks = self._generate_knowledge_tasks(campaign_id, phase, meta)
        elif campaign_type == 'FITNESS_ARC':
            tasks = self._generate_fitness_arc_tasks(campaign_id, phase, meta)
        
        # Insert tasks into agent_tasks and link to campaign
        task_ids = []
        for task in tasks:
            # Get next task_id
            max_id = conn.execute("SELECT MAX(task_id) FROM agent_tasks").fetchone()[0]
            next_id = (max_id or 0) + 1
            
            conn.execute("""
                INSERT INTO agent_tasks (task_id, agent_name, task_type, task_data, status, priority)
                VALUES (?, ?, ?, ?, 'pending', ?)
            """, [
                next_id,
                task['agent_name'],
                task['task_type'],
                json.dumps(task['task_data']),
                task.get('priority', 5)
            ])
            
            # Link to campaign
            conn.execute("""
                INSERT INTO campaign_tasks (campaign_id, task_id, phase)
                VALUES (?, ?, ?)
            """, [campaign_id, next_id, phase])
            
            task_ids.append(next_id)
        
        conn.close()
        
        print(f"📋 Generated {len(tasks)} tasks for {campaign_id} / {phase}")
        
        return task_ids
    
    def _generate_codebase_tasks(self, campaign_id: str, phase: str, meta: Dict) -> List[Dict]:
        """Generate tasks for Codebase Overhaul campaign"""
        repo_path = meta.get('repo_path', '.')
        
        if phase == CampaignPhase.MAPPING:
            return [
                {
                    'agent_name': 'Harvester',
                    'task_type': 'map_repo_structure',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'repo_path': repo_path,
                        'phase': phase
                    },
                    'priority': 7
                },
                {
                    'agent_name': 'Coder',
                    'task_type': 'extract_todos',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'repo_path': repo_path,
                        'patterns': ['TODO', 'FIXME', 'HACK', 'NOTE', 'XXX'],
                        'phase': phase
                    },
                    'priority': 7
                },
                {
                    'agent_name': 'Librarian',
                    'task_type': 'embed_key_modules',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'repo_path': repo_path,
                        'phase': phase
                    },
                    'priority': 6
                }
            ]
        
        elif phase == CampaignPhase.ANALYSIS:
            return [
                {
                    'agent_name': 'Oracle',
                    'task_type': 'analyze_hotspots',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'metrics': ['complexity', 'size', 'todo_density'],
                        'phase': phase
                    },
                    'priority': 7
                },
                {
                    'agent_name': 'Guardian',
                    'task_type': 'static_check',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'checks': ['dangerous_patterns', 'inconsistencies'],
                        'phase': phase
                    },
                    'priority': 6
                }
            ]
        
        elif phase == CampaignPhase.PROPOSAL:
            return [
                {
                    'agent_name': 'Coder',
                    'task_type': 'generate_refactor_plan',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'target': 'top_hotspots',
                        'phase': phase
                    },
                    'priority': 6
                },
                {
                    'agent_name': 'Alchemist',
                    'task_type': 'generate_docs_outline',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'style': 'technical',
                        'phase': phase
                    },
                    'priority': 5
                }
            ]
        
        elif phase == CampaignPhase.MONITORING:
            return [
                {
                    'agent_name': 'Oracle',
                    'task_type': 'monitor_refactor_impact',
                    'task_data': {
                        'campaign_id': campaign_id,
                        'phase': phase
                    },
                    'priority': 5
                }
            ]
        
        return []
    
    def _generate_knowledge_tasks(self, campaign_id: str, phase: str, meta: Dict) -> List[Dict]:
        """Generate tasks for Knowledge Archive campaign"""
        # TODO: Implement knowledge archive task generation
        return []
    
    def _generate_fitness_arc_tasks(self, campaign_id: str, phase: str, meta: Dict) -> List[Dict]:
        """Generate tasks for Fitness Arc campaign"""
        # TODO: Implement fitness arc task generation
        return []
    
    def advance_phase(self, campaign_id: str) -> str:
        """Move campaign to next phase"""
        conn = duckdb.connect(self.db_path)
        
        current_phase = conn.execute("""
            SELECT current_phase FROM campaigns WHERE campaign_id = ?
        """, [campaign_id]).fetchone()[0]
        
        # Phase progression
        phase_order = [
            CampaignPhase.MAPPING,
            CampaignPhase.ANALYSIS,
            CampaignPhase.PROPOSAL,
            CampaignPhase.EXECUTION,
            CampaignPhase.MONITORING
        ]
        
        try:
            current_idx = phase_order.index(current_phase)
            next_phase = phase_order[current_idx + 1] if current_idx + 1 < len(phase_order) else CampaignPhase.MONITORING
        except ValueError:
            next_phase = CampaignPhase.MAPPING
        
        conn.execute("""
            UPDATE campaigns
            SET current_phase = ?, updated_at = CURRENT_TIMESTAMP
            WHERE campaign_id = ?
        """, [next_phase, campaign_id])
        
        conn.close()
        
        print(f"⏭️  Campaign {campaign_id}: {current_phase} → {next_phase}")
        
        return next_phase
    
    def get_campaign_status(self, campaign_id: str) -> Dict:
        """Get detailed campaign status"""
        conn = duckdb.connect(self.db_path)
        
        # Campaign details
        campaign = conn.execute("""
            SELECT name, status, goal, current_phase, created_at, meta
            FROM campaigns
            WHERE campaign_id = ?
        """, [campaign_id]).fetchone()
        
        if not campaign:
            conn.close()
            return {}
        
        # Task counts by phase
        task_counts = conn.execute("""
            SELECT phase, COUNT(*) as cnt
            FROM campaign_tasks
            WHERE campaign_id = ?
            GROUP BY phase
        """, [campaign_id]).fetchall()
        
        # Completed tasks
        task_ids = [str(tid) for tid, in conn.execute("""
            SELECT task_id FROM campaign_tasks WHERE campaign_id = ?
        """, [campaign_id]).fetchall()]
        
        if task_ids:
            placeholders = ','.join(['?'] * len(task_ids))
            completed = conn.execute(f"""
                SELECT COUNT(*) FROM agent_tasks 
                WHERE task_id IN ({placeholders}) AND status = 'completed'
            """, task_ids).fetchone()[0]
        else:
            completed = 0
        
        conn.close()
        
        return {
            'campaign_id': campaign_id,
            'name': campaign[0],
            'status': campaign[1],
            'goal': campaign[2],
            'current_phase': campaign[3],
            'created_at': campaign[4],
            'meta': json.loads(campaign[5]) if campaign[5] else {},
            'tasks_by_phase': {phase: count for phase, count in task_counts},
            'tasks_completed': completed
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Campaign Coordinator')
    parser.add_argument('action', choices=['init', 'create', 'list', 'status', 'advance', 'generate'],
                       help='Action to perform')
    parser.add_argument('--campaign-id', help='Campaign ID')
    parser.add_argument('--name', help='Campaign name')
    parser.add_argument('--goal', help='Campaign goal')
    parser.add_argument('--type', choices=['CODEBASE_OVERHAUL', 'KNOWLEDGE_ARCHIVE', 'FITNESS_ARC'],
                       help='Campaign type')
    parser.add_argument('--repo-path', default='.', help='Repo path for codebase campaigns')
    parser.add_argument('--phase', help='Phase to generate tasks for')
    parser.add_argument('--db', default='evidence.duckdb', help='Database path')
    
    args = parser.parse_args()
    
    coordinator = CampaignCoordinator(db_path=args.db)
    
    if args.action == 'init':
        print("✅ Campaign system initialized")
    
    elif args.action == 'create':
        if not all([args.campaign_id, args.name, args.goal, args.type]):
            print("❌ Error: --campaign-id, --name, --goal, --type required")
            return 1
        
        meta = {'type': args.type}
        if args.type == 'CODEBASE_OVERHAUL':
            meta['repo_path'] = args.repo_path
        
        coordinator.create_campaign(args.campaign_id, args.name, args.goal, args.type, meta)
    
    elif args.action == 'list':
        campaigns = coordinator.get_active_campaigns()
        print(f"\n📋 Active Campaigns ({len(campaigns)}):\n")
        for c in campaigns:
            print(f"  {c['campaign_id']}: {c['name']}")
            print(f"    Phase: {c['current_phase']}")
            print(f"    Goal: {c['goal'][:80]}...")
            print()
    
    elif args.action == 'status':
        if not args.campaign_id:
            print("❌ Error: --campaign-id required")
            return 1
        
        status = coordinator.get_campaign_status(args.campaign_id)
        if status:
            print(f"\n📊 Campaign Status: {status['campaign_id']}\n")
            print(f"  Name: {status['name']}")
            print(f"  Status: {status['status']}")
            print(f"  Phase: {status['current_phase']}")
            print(f"  Completed: {status['tasks_completed']} tasks")
            print(f"\n  Tasks by Phase:")
            for phase, count in status['tasks_by_phase'].items():
                print(f"    {phase}: {count}")
    
    elif args.action == 'advance':
        if not args.campaign_id:
            print("❌ Error: --campaign-id required")
            return 1
        
        next_phase = coordinator.advance_phase(args.campaign_id)
        print(f"✅ Advanced to {next_phase}")
    
    elif args.action == 'generate':
        if not all([args.campaign_id, args.phase]):
            print("❌ Error: --campaign-id and --phase required")
            return 1
        
        task_ids = coordinator.generate_phase_tasks(args.campaign_id, args.phase)
        print(f"✅ Generated {len(task_ids)} tasks")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
