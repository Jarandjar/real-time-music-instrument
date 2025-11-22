#!/usr/bin/env python3
"""Quick script to view campaign tasks"""

import duckdb
import json

conn = duckdb.connect('evidence.duckdb', read_only=True)

tasks = conn.execute("""
    SELECT task_id, agent_name, task_type, priority, task_data 
    FROM agent_tasks 
    WHERE task_id IN (SELECT task_id FROM campaign_tasks WHERE campaign_id='codebase_main') 
    ORDER BY priority DESC, task_id DESC
""").fetchall()

print('\n📋 Campaign Tasks (codebase_main):\n')
for t in tasks:
    task_id, agent, task_type, priority, data = t
    data_dict = json.loads(data)
    print(f'  {task_id}: {agent} → {task_type} (priority {priority})')
    print(f'     Phase: {data_dict.get("phase", "?")}')
    print(f'     Repo: {data_dict.get("repo_path", "?")}')
    print()

conn.close()
