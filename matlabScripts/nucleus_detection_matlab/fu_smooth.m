function ys=fu_smooth(y,opt)

%ys=fu_smooth(y,opt)
%bracket for smoothing
%faster but less flexible than fu_smoothing
%y: vector
% opt.mtd    % as in fun smooth (+ 'none')
%    .wl     % window length
%    .order  % polynomial order for sgolay


if nargin<1; opt=struct; end
opt=fu_optstruct_init(opt,{'mtd' 'wl' 'order'},{'mova' 5 3});

if strcmp(opt.mtd,'none')
  ys=y;
elseif ~strcmp(opt.mtd,'sgolay')
   ys=smooth(y,opt.wl,opt.mtd);
else
   ys=smooth(y,opt.wl,opt.mtd,opt.order);
end

return
