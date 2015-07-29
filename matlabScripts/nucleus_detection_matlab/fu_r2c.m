function [v t]=fu_r2c(v)

%v=fu_r2c(v)
%[v t]=fu_r2c(v)
%if V is a ROW VECTOR, it is transposed and T is set to 1
%needed for uniform vector/matrix treatment in functions
%operating on column vectors
%see also fu_c2r, fu_transpose

tb=0;
% transpose row vector
if size(v,1)==1
   v=v';
   tb=1;
end

if nargout==2
  t=tb;
end

return
