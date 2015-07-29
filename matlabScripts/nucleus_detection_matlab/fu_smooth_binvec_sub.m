function v=fu_smooth_binvec_sub(v,b,l);

%called by fu_smooth_binvec

r = abs(b-1);
i = find(v==b);
if length(i)==0; return; end
di = [1 diff(i)];
seq_i=[];
for j=1:length(di)
    if di(j)>1
        if length(seq_i) < l
            v(seq_i)=r;
        end
        seq_i=[];
    end
    seq_i=[seq_i i(j)];
end

% last seq
if length(seq_i) < l; v(seq_i)=r; end

return
