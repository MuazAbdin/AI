30057529
31497638
*****
Comments:
DESCRIPTION of better evaluation function:
We used 5 heuristics:
1. score: the current state score, the higher the score, the better the state.
2. empty tiles: how many empty tiles the current state has, the more free tiles,
                the more likely to last longer.
3. uniformity: the number of tiles with uniform value, the more uniform tiles,
               the more likely to execute merges.
4. cluster: of different-value adjacent tiles, the bigger the cluster, the less
            likely to execute merges.
5. monotonicity: is there an order between the tiles? is the values order in
                 decreasing or increasing manner upon the rows or columns.
