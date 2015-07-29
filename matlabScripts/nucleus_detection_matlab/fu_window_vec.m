function m = fu_window_vec(v,opt);

% m = fu_window_vec(v,opt);
% windows vector V according to specs in struct opt
% V: input vector
% M: matrix, one window per row
% OPT:
%   .sts: <1> int, step size
%   .wl: <1> int, window length

% opt init
% idx is needed for fu_window_bnd, not to be specified by user
%usable for vectorisation of algorithms

if nargin<2; opt=struct; end
opt = fu_optstruct_init(opt,{'sts' 'wl'},{1 1});
opt.idx=1;
wb = fu_window_bnd(opt.wl,length(v),opt);

m=v(wb);

return
