function vs = fu_smooth_binvec(v,l);

% vs = fu_smooth_binvec(v,l);
% v: binary vector
% l: minimum length of 1- or 0-subsequences
% vs: smoothed vector (short subsequences get same value as neighbors)
% e.g. v = [1 1 1 1 0 0 1 1 1 1];
%      l = 3
% --> vs = [1 1 1 1 1 1 1 1 1 1];

[vs tt] = fu_transp(v,'r');

vs = fu_smooth_binvec_sub(vs,1,l);
vs = fu_smooth_binvec_sub(vs,0,l);

vs=fu_transp(vs,tt);

return
