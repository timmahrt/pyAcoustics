function [xt done] = fu_transp(x,do)

% xt = fu_transp(x,do)
% [xt done] = fu_transp(x,do)
% x: vector
% do: <'t'>|'r'|'c'|'i' - transpose, make row, make column, ignore
%       'r' and 'c' just make sense for vectors!!
%       input 1|0 is mapped to 't'|'i' for backward compatibility
% xt: x +/- transposed
% done: 't' if transformation was carried out, else 'i' (for consistent
%       reapplication of fu_transpose_vec)
% Of use e.g. if a function would need a column vector as input without
% bothering the user and returning a vector in the same format as the input
% See example in fu_smooth_binvec.m

if nargin<2; do='t'; end
if isnumeric(do)
    if do==1; do='t';
    else do='i';
    end
end

dun='i';
xt=x;

if strcmp(do,'t')
    xt=x';
    dun=do;
elseif ~strcmp(do,'i')
    s=size(x);
    if min(s) > 1
        disp('Transposition just applicable for vectors. Done nothing.');
    else
        if ((strcmp(do,'r') && s(2)==1) || (strcmp(do,'c') && s(1)==1))
            xt=x';
            dun='t';
        end
    end
end

if nargout > 1; done=dun; end

return
