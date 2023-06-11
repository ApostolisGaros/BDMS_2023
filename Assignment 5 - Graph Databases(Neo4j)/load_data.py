from py2neo import Graph
import pandas as pd
import time
# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))  # replace with your actual password


datasetFolder = 'dataset/act-mooc/'
# Load data from .tsv files
actions = pd.read_csv(datasetFolder + 'mooc_actions.tsv', sep='\t')
features = pd.read_csv(datasetFolder + 'mooc_action_features.tsv', sep='\t')
labels = pd.read_csv(datasetFolder + 'mooc_action_labels.tsv', sep='\t')

# Merge dataframes
data = pd.merge(actions, features, on='ACTIONID')
data = pd.merge(data, labels, on='ACTIONID')

# Create User and Target nodes
users = list(data['USERID'].unique())
targets = list(data['TARGETID'].unique())

# Convert to fload
users = [float(i) for i in users]
targets = [float(i) for i in targets]

print("Inserting users")
# graph.run("UNWIND $users AS user_id MERGE (:User {id: user_id})", users=users)
print("Inserting targets")
# graph.run("UNWIND $targets AS target_id MERGE (:Target {id: target_id})", targets=targets)


print("Creating indexes")
# Create indexes on User and Target nodes to run MATCH queries faster
# graph.run("CREATE INDEX FOR (n:User) ON (n.id)")
# graph.run("CREATE INDEX FOR (n:Target) ON (n.id)")

# Create Action relationships
actions = list(data.to_dict('records'))
actions = [dict((k, float(v)) for (k, v) in d.items()) for d in actions]


print("Inserting actions")
# graph.run("""
# UNWIND $actions AS action
# MATCH (user:User {id: action.USERID}), (target:Target {id: action.TARGETID})
# MERGE (user)-[:ACTION {id: action.ACTIONID, feature2: action.FEATURE2, label: action.LABEL}]->(target)
# """, actions=actions)