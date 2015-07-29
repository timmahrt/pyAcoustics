function vt = fu_trim_vec(v,w,a);

% vt=fu_trim_vec(v,w,e);
% pops vector V or pushes scalar/vector A to V until size of V is equal to
% size of W

vt=column2rowvec(v);
while length(vt)<length(w)
    vt=[vt a];
end

vt=vt(1:length(w));

if size(vt,1) ~= size(w,1)
    vt=vt';
end

return
