function [voi zrr] = fu_voicing(y,sr,opt);

% voi = fu_voicing(y,sr <,opt>);
% [voi zr] = fu_voicing(y,sr <,opt>);
% Y: signal
% SR: sample rate
% VOI: vector with 1 element per window
%   1: voiced
%   0: voiceless/pause
% ZR: do=='apply': vector of zero crossing rates, one value per window
%         'train': opt struct with optimised .th and .zr_th and .err error
% OPT:
%   .do: <apply>|train
%   .wl: window length <0.03> (<1: in s, >=1: in samples)
%   .th: <0.002> relative amplitude threshold, y<max*.th is ignored
%   .sts: step size <0.01> (<1: in s, >=1: in samples)
%   .zr_th: <2000> (below & >0: voiced; use higher value for increased
%           recall, lower value for increased precision)
%   .min_nf: <3> (min number of frames in a row to be constantly
%                 (un)voiced. Interpolation over shorter sequences
%   .ret: <'w'>|'smpl'
%            'w': one value per window
%            'smpl': one value per signal sample
%  IF .do equal 'train'
%   .errfun <@fu_voicing_err>
%   .ref: reference matrix or vector (see e.g. voi_ref.dat)
%   --> optimisation of .th and .zr_th
%   integrated training call by FU_VOI_OPTIM_BRACKET
%
% voicing detection by zero crossing rate
% BEWARE: Default parameters are optimised on si1000p reference and
% sts=0.01. If step size is changed, than $sts in sncl_ref.pl has to
% be changed the same way!!!
% param values are informally optimised on SI1000P reference data:
%   hamming: 0.1180
% precision: 0.8898
%    recall: 0.9045

if nargin < 3; opt=struct; end
opt = fu_optstruct_init(opt,{'wl' 'th' 'sts' 'zr_th' 'do' 'min_nf' 'ret'},...
                            {0.03 0.002 0.01 2000 'apply' 3 'w'});
opt.sr = sr;


if strcmp(opt.do,'apply')  %%%% application
    [voi zr] = fu_voicing_sub(y,opt);
    if nargout==2; zrr=zr; end
else   %%%%%%%%%%%%%%%%%%%%%%%% training
    %o_opt=optimset(@fminunc);
    o_opt=optimset(@fminsearch);
    o_opt=optimset('LargeScale','on');
    w0=[0.004 1000];
    %[w fval ef o]=fminunc(opt.errfun,w0,o_opt);
    [w fval ef o]=fminsearch(opt.errfun,w0,o_opt);
    opt.th=w(1);
    opt.zr_th=w(2);
    [voiv zr] = fu_voicing_sub(y,opt);
    % error
    voiv=fu_trim_vec(voiv,opt.ref,0);
    e = pdist([voiv;opt.ref],'hamming');
    voi=opt;
    voi.err=e;
    if nargout==2; zrr=e; end % to avoid crash
end

return
