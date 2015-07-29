function wb = fu_window_bnd(wl,ly,opt);

%wb = fu_window_bnd(wl,ly,opt);
%returns matrix of window on- and offset indices (one pair per row)
%windows are centered on each index 1:opt.sts:ly
% wl: window length
% ly: length of vector
% opt:
%   .sts: int <1> - step size
%   .idx: <0>|1   - if one not just bounds but also all indices between
% e.g. wl=2; ly=6; opt.sts=1; opt.idx=0;
% --> wb = [1 2; 1 3; 2 4; 3 5; 4 6; 5 6]
%                             opt.idx=0;
% --> wb = [1 1 2; 1 2 3; 2 3 4; 3 4 5; 4 5 6; 5 6 6]
%usable for vectorisation of algorithms

if nargin<3; opt=struct; end
opt = fu_optstruct_init(opt,{'sts' 'idx'},{1 0});

x=[1:opt.sts:ly]';
h=round(wl/2);

if opt.idx==0
    hh = [-h h];
else
    hh= -h:h;
end

wb=repmat(hh,size(x,1),1)+repmat(x,1,size(hh,2));
wb(find(wb<1))=1;
wb(find(wb>ly))=ly;

return
