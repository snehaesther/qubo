# QUBO Formulation for Path Optimization

## Overview

This document presents two Quadratic Unconstrained Binary Optimization (QUBO) formulations for a path selection problem as we presented in the meeting today:

1. Basic formulation with fixed source and sink nodes  
2. Advanced formulation where the source and sink are automatically selected  

The formulation also addresses the "two minima issue", which arises when modeling logical OR conditions in quadratic form.

---

1. Basic QUBO Formulation (Fixed Source and Sink)

## Formula

$$E(x,y) =
\sum_{e \in E} c_e x_e
+ P_1 \sum_{v \in V} \left( \sum_{e \in \delta(v)} s_{v,e} x_e - T_v \right)^2
+ P_2 \sum_{v \in V} \left( \sum_{e \in \delta(v)} x_e - 2y_v \right)^2$$

---

## Decision Variables

- $x_e \in \{0,1\}$: Indicates whether edge $e$ is selected  
- $y_v \in \{0,1\}$: Indicates whether node $v$ is active  

---

## Parameters

- $c_e$: Cost (weight) of edge $e$  
- $P_1, P_2$: Large penalty coefficients  

---

## Flow Direction Coefficient

$$
s_{v,e} =
\begin{cases}
+1 & \text{if edge } e \text{ leaves node } v \\
-1 & \text{if edge } e \text{ enters node } v
\end{cases}
$$

---

## Node Type Definition

$$
T_v =
\begin{cases}
+1 & \text{if } v \text{ is the source node} \\
-1 & \text{if } v \text{ is the sink node} \\
0 & \text{otherwise}
\end{cases}
$$

---

## Interpretation of Each Term

### 1. Cost Term

$$
\sum_{e \in E} c_e x_e
$$

Minimizes the total cost of selected edges.

---

### 2. Flow Constraint

$$
\left( \sum_{e \in \delta(v)} s_{v,e} x_e - T_v \right)^2
$$

Ensures flow conservation:
- Source node: net flow = +1  
- Sink node: net flow = -1  
- Intermediate nodes: net flow = 0  

---

### 3. Edge Count Constraint (Two Minima Solution)

$$
\left( \sum_{e \in \delta(v)} x_e - 2y_v \right)^2
$$

### The Two Minima Issue

A valid node must satisfy one of the following conditions:

- The node has 0 edges (inactive node)  
- The node has exactly 2 edges (active node in the path)  

This represents a logical OR condition:

(node has 0 edges) OR (node has 2 edges)

A quadratic function cannot directly represent two separate minima. Therefore, an auxiliary binary variable is introduced as suggested by stefan.

---

### Solution Using Auxiliary Variable

- $y_v = 0$: node is inactive and must have 0 edges  
- $y_v = 1$: node is active and must have 2 edges  

The constraint enforces:

$$
\sum x_e = 2y_v
$$

This ensures only the following cases are valid:

| $y_v$ | Number of edges |
|------|----------------|
| 0    | 0              |
| 1    | 2              |

---

## Importance of This Constraint

This constraint prevents:
- extra edges  
- loops  
- invalid path structures  

It ensures that each node is either unused or correctly part of a path.

---

# 2. Advanced QUBO Formulation (Automatic Source and Sink Selection)

## Formula

$$
E(x,y,z) =
\sum_{e \in E} c_e x_e
+ P_1 \sum_{v \in V} \left( \sum_{e \in \delta(v)} s_{v,e} x_e - (z_v^+ - z_v^-) \right)^2
+ P_2 \sum_{v \in V} \left( \sum_{e \in \delta(v)} x_e - 2y_v \right)^2
+ P_3 \left( \sum_{v \in V} z_v^+ - 1 \right)^2
+ P_4 \left( \sum_{v \in V} z_v^- - 1 \right)^2
$$

---

## Additional Variables

- $z_v^+ \in \{0,1\}$: Indicates node $v$ is selected as the source  
- $z_v^- \in \{0,1\}$: Indicates node $v$ is selected as the sink  

---

## Interpretation

### Flow Relation

$$
\sum s_{v,e} x_e = z_v^+ - z_v^-
$$

This means:
- +1 → node becomes source  
- -1 → node becomes sink  
- 0 → node is intermediate  

---

### Source Constraint

$$
\left( \sum_{v} z_v^+ - 1 \right)^2
$$

Ensures exactly one source node.

---

### Sink Constraint

$$
\left( \sum_{v} z_v^- - 1 \right)^2
$$

Ensures exactly one sink node.

---

## This is suggested because :

- The model automatically determines the start and end nodes  
- Enables more flexible optimization  

---

# 3. Summary

## Basic Model
- Source and sink are predefined  

## Advanced Model
- Source and sink are selected automatically  
---
