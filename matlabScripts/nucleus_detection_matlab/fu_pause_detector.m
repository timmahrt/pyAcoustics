function t = fu_pause_detector(s,opt);

% t = fu_pause_detector(s,opt);
% looks for pauses in signal according to criterias
% specified in opt
% input: s - signal vector
%        opt - structure with fields
%           .length: minimum length of pause in s
%           .rlength: length of reference window in s
%           .f_thresh: threshold factor (*rmse(reference_window))
%           .fs: sample rate
%           .ret: <'s'>|'smpl' return values in seconds or samples
%       default (optimised on IMS radio news corpus, read speech,
%             by fminunc()):    
%           opt.length = 0.1524;
%           opt.f_thresh = 0.0767;
%           opt.rlength = 5;
%           opt.fs = 16000;
% output: t - matrix of pause time on- and offsets (in s)
% algorithm:
% - preprocessing: removing DC, low pass filtering (10kHz)
% - window y with opt.length sec is moved over signal with stepsize
%   0.05 s
% - reference window rw with opt.rlength sec centered on y midpoint
%   is moved in parallel
% - if rmse(rw) < rmse(global_signal)*opt.f_thresh
%       rw is set to global_signal (long pause assumed)
% - if rmse(y) < rmse(rw)*opt.f_thresh
%       y is considered as a pause
% Uwe Reichel, IPS (2009)


%%%% defaults %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if nargin==1; opt=struct; end
ofld={'f_thresh' 'length' 'rlength' 'fs' 'ret'};
odef={0.0767 0.1524 5 16000 's'};
opt=fu_optstruct_init(opt,ofld,odef);


%%%% preprocessing %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% stereo->mono, mean 0
s = s(:,1)-mean(s(:,1));
% low pass filtering (just carried out if fs > 20kHz)
s = fu_filter(s,'low',10000,opt.fs);


%%%% settings %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% reference window span
rws = floor(opt.rlength*opt.fs);
% signal length
ls=length(s);
% min pause length in samples
ml=floor(opt.length*opt.fs);
% global rmse and pause threshold
e_glob = fu_rmse(s);
t_glob = opt.f_thresh*e_glob;
% stepsize
%sts=floor(ml/4);
sts=max(1,floor(0.05*opt.fs));
stsh=floor(sts/2); % for centering of reference window


%%%% pause detection %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% output array collecting pause sample indices
t=[];
j=1;


for i=1:sts:ls
    %%%% window %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    yi=i:min(ls,i+ml-1);
    %tt=[yi(1) yi(end)]
    y=s(yi);
    e_y = fu_rmse(y);
    %%%% reference window %%%%%%%%%%%%%%%%%%%
    rw=s(fu_i_window(min(i+stsh,ls),rws,ls));
    e_rw=fu_rmse(rw);
    if (e_rw <= t_glob); e_rw=e_glob; end
    %%%% if rmse in window below threshold %%
    if e_y <= e_rw*opt.f_thresh
        if size(t,1)==j
            % values belong to already detected pause
            if yi(1) < t(j,2)
                t(j,2)=yi(end);
            else                          % new pause
                j=j+1;
                t(j,:)=[yi(1) yi(end)];
            end
        else                              % new pause
            t(j,:)=[yi(1) yi(end)];
        end
    end
end


%%%%%% conversion of sample indices into %%%%%%%%%%%%%%
%%%%%% time on- and offset values (sec) %%%%%%%%%%%%%%%

if strcmp(opt.ret,'s'); t=t./opt.fs; end

return
