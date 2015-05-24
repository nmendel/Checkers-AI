--- play.py	Mon Mar  2 22:57:47 2015
+++ play _latenight.py	Mon Mar  2 22:55:37 2015
@@ -39,7 +39,7 @@
                    [BLACK, 0, BLACK, 0, BLACK, 0, BLACK, 0]]
     aiPlaying = True
 
-    best_move_score = None
+    all_moves = None
     multi_jump = None
 
     def __init__(self, numPlayers=1):
@@ -145,11 +145,11 @@
         else:
             next = 2
 
-        self.best_move_score = None
         pprint(self.board)
 
     def look_ahead(self, board, color):
         depth = LOOK_AHEAD - 1
+        #self.all_
         moves, m2 = self.find_all_moves(board, color)
         self.expand_nodes(moves, (color % 2) + 1, depth - 1, MIN, m2)
         return moves, m2
@@ -159,6 +159,7 @@
         if depth == 0:
             score = True
 
+        local_best_move_score = None
         for move, cdr in moves.items():
             b = cdr[0]
 
@@ -167,6 +168,7 @@
             m, m2 = self.find_all_moves(b, color, score, depth)
             cdr.append(m)
             cdr2.append(m2)
+   
 
             if depth:
                 self.expand_nodes(m, (color % 2) + 1,
@@ -176,9 +178,17 @@
                 cdr[1] = bestScore
                 cdr2[1] = getScores(m2, minmax)
 
-                if self.best_move_score == None or bestScore > self.best_move_score:
-                    self.best_move_score = bestScore
-
+            # AB Pruning
+                """
+            if local_best_move_score == None \
+                    or cdr[1] >= local_best_move_score:
+                local_best_move_score = cdr[1]
+                cdr.append(m)
+                cdr2.append(m2)
+            else:
+                # pruned
+                pass
+"""
 
 
     def find_all_moves(self, board, color, score=False, depth=0):
@@ -338,9 +348,9 @@
         for i, row in enumerate(board):
             for j, piece in enumerate(row):
                 if piece in (RED, RKING):
-                    redScore += piece + 1 + self.getPositionValue(i, j)
+                    redScore += ((piece + 1) * 2) + self.getPositionValue(i, j)
                 elif piece in (BLACK, BKING):
-                    blackScore += piece + self.getPositionValue(i, j)
+                    blackScore += (piece * 2) + self.getPositionValue(i, j)
 
         s = (redScore * -1) + blackScore
         return s
@@ -380,21 +390,15 @@
 
 def getScores(m, minmax):
     bestVal = None
-    localBest = None
 
     for _, cdr in m.items():
+        #if len(cdr) < 3:
+        #    continue
         for _, rest in cdr[2].items():
             if bestVal == None or \
                     (minmax == MIN and rest[1] < bestVal) or \
                     (minmax == MAX and rest[1] > bestVal):
                 bestVal = rest[1]
-            if localBest == None or \
-                    (minmax == MIN and rest[1] < localBest) or \
-                    (minmax == MAX and rest[1] > localBest):
-                localBest = rest[1]
-                
-        cdr[1] = localBest
-        localBest = None
         
     return bestVal
 
