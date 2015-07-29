function e = fu_rmse(x,y)

%e = fu_rmse(x)
%e = fu_rmse(x,y)
%returns root mean squared error E between vector X and 0-line
%or root mean squared error E between vectors X and Y

if nargin < 2
  e=sqrt(sum(x.^2)/length(x));
else
  e=sqrt(sum((x-y).^2)/length(x));
end

return
