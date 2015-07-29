function sb = fu_sylbnd(s,sn,opt)

%sb = fu_sylbnd(s,sn,opt)
%called in fu_sylncl
%s: signal vector
%sn: vector with detected nucleus samples (by fu_sylncl_sub)
%opt: as provided for fu_sylncl

% window length for energy calculation in samples
ml=floor(opt.length*opt.fs);
% stepsize
sts=max(1,floor(0.03*opt.fs));

sb=[];
for i=1:length(sn)-1;  % for all adjacent syl ncl
    on=sn(i);
    off=sn(i+1);
    sw = s(on:off);
    ls = length(sw);
    all_i=[];
    all_e=[];
    for j=1:sts:length(sw)  % for all windows within ncl pair
        yi=fu_i_window(j,ml,ls);
        y = sw(yi);
        e_y = fu_rmse(y);
        all_i=[all_i j];
        all_e=[all_e e_y];
    end
    [ymin ymini] = min(all_e);
    sb = [sb; on+all_i(ymini(1))];
end

return
