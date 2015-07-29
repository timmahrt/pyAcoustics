function v=row2columnvec(v)

if length(v)==0; return; end

if length(v(:,1))==1
    v=v';
end

return
