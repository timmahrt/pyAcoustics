function [pks idx] = fu_locmax(y,opt);

%[pks idx] = fu_locmax(y,opt);
%wrapper around 'findpeaks'
%y: data vector
%opt:
%   .smooth.win <1> smoothing options, see fu_smooth
%          .mtd <'none'>
%          .order <1>
%   .peak.mph: <-Inf>  min peak height
%          .th: <0>  threshold; min difference of local peak to neighbors
%          .mpd: <1> min peak distance
%   .verbose.plot: <0>|1
%           .bw: <0>|1
%pks: peak values
%idx: their positions [sample]

%% init
if nargin<2; opt=struct; end

opt=fu_optstruct_init(opt,{'smooth' 'peak'},{struct struct});
opt.smooth=fu_optstruct_init(opt.smooth,{'win' 'mtd' 'order'},{1 'none' 1});
opt.peak=fu_optstruct_init(opt.peak,{'mph' 'th' 'mpd'},{-Inf 0 1});

%% locmax
opt.peak.mpd=min(opt.peak.mpd,length(y)-1);

[pks idx] = findpeaks(fu_smooth(y,opt.smooth),...
            'MINPEAKDISTANCE',opt.peak.mpd,'MINPEAKHEIGHT',opt.peak.mph,...
            'THRESHOLD',opt.peak.th);

% fallback
if length(pks)==0
    [pks idx] = findpeaks(y);
end

% transpose to column vector since in 7.10.0 findpeaks() always returns
% row vector!
if size(y,2)==1
    pks=fu_r2c(pks);
    idx=fu_r2c(idx);
end

return
