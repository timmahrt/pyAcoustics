function zr = fu_zero_crossing_rate(y,sr,opt);

%zr = fu_zero_crossing_rate(y,sr [,opt]);
%y: signal vector
%sr: sample rate (<16000>)
%opt
%   .wl: <0.01> window length (<1: in s, >=1: in samples)
%   .th: <0.004> min abs extreme point amplitude (vs. noise in <p:>)
%        used as a factor: .th * max(abs(y)) !
%   .sts: step size <1> (<1: in s, >=1: in samples)
%zr: zero crossing rate in crossing/sec (same length as Y)
% set all data points below .th to NaN
% 
% center window of length .wl on each data point in Y
% 

if nargin < 2; sr=16000; end
if nargin < 3; opt=struct; end
opt=fu_optstruct_init(opt,{'wl' 'th' 'sts'},{0.01 0.004 1});

% sec -> samples
if opt.wl < 1; opt.wl = round(opt.wl*sr); end
if opt.sts < 1; opt.sts = round(opt.sts*sr); end

% filter values below threshold
ya=abs(y);
y(find(ya<opt.th*max(ya)))=NaN;

% multiplying subsequent data points: <=0 -> zero crossing
zcv = [NaN; row2columnvec(y(1:end-1).*y(2:end))];

% -> matrix, one row per window
zcm = fu_window_vec(zcv,opt);

% zero crossings
[ri ci] = find(zcm<=0);

% how many zero crossings per window?
zcw = fu_typecount(ri);

% getting rate
l=size(zcm,2);

zr=zeros(size(zcm,1),1);
zr(zcw(:,1)) = zcw(:,2) / l * sr;

return
