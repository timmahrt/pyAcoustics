function tc = fu_typecount(v)

%tc = fu_numcount(v)
%returns counts of each type in vector V in matrix TC
%TC: each row contains 'type count'-pair, types are sorted
%usable for vectorisation of algorithms

[vs i j] = unique(sort(row2columnvec(v)));

d=diff([0;i]);

tc=[vs d];

return
