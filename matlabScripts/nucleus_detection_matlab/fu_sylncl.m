function [sn sb] = fu_sylncl(s,opt);

% sn = fu_sylncl(s,opt);
% [sn sb] = fu_sylncl(s,opt);
% opt.do='apply':
%  default case.
%  returns vector sn of syllable nucleus samples in speech signal s
%  given opt structure with fields as specified in training output below.
%  Optionally, sb, a vector of syllable boundary samples is returned
%  (simply the sample minimum energy between two adjacent nuclei)
% opt.do='train':
%   .ref: sample reference
%   .fs: sample frequency
%   .errtype: <'f'>|'io'|'mae'
%       error type: 1-fscore (best choice)
%                   n_ins+n_omis (used in diss)
%                   1-MAE (after alignment)
%  returns structure SN to be used as OPT in 'apply' case
%   .f_thresh: energy threshold factor
%   .bf: lower and upper boundary frequencies for band pass filtering
%   .do: 'apply'
%   .fs: sample frequency of input signal
%   .e_min: minimum needed proportion of max energy
%   .length: length of energy window in s
%   .rlength: length of reference energy window (>length) in s
%   .md: min distance between subsequent nuclei in s (set to 0 if to be
%       neglected)
%   .nouse_int: <[]>; n x 2 matrix [on off] of intervals not to be used
%        (e.g. pause intervals). In samples! E.g. output of
%        fu_pause_detector (with opt.ret='smpl'). Additionally,
%        0-output of fu_voicing (to be transformed for compatibility) can
%        be used. Both can also be called inline setting .do_nouse>0
%   .do_nouse: <0>|1|2|3: create or enlarge .nouse_int matrix by
%       finding pauses and/or voiceless utterance parts
%            <0> - do nothing
%            1 - detect pauses and voiceless utterance parts
%            2 - pause only
%            3 - voiceless utterance parts only
%   .verbose: plot signal and nuclei
%
% -- exclude pause and voiceless intervals from analysis?
% opt.pau.do=<'apply'>|'skip': prceeding
%        .* see matlab_lib/fu_pause_detector.m
% opt.voi.do=<'apply'>|'skip': preceeding voicing detection
%        .*: see fu_voicing.m
%
% minimal application example:
% [y fs] = wavread('myaudio.wav');
% opt.fs = fs;
% opt.verbose = 1;
% [sn sb] = fu_sylncl(y,opt);

global s_glob;
global opt_glob;
close all

if nargin==1; opt=struct; end
opt=fu_optstruct_init(opt,{'do' 'nouse_int' 'do_nouse' 'errtype'},{'apply' [] 2 'f'});
ofld={'do' 'bf' 'f_thresh' 'length' 'rlength' 'md' 'e_min' 'fs' ...
    'verbose' 'pau' 'unv'};


% preprocessing -> defining intervals not usable for syllable nuclei
% matrix, rows: on- and offset in samples
%opt.nouse_int = fu_sylncl_no_use_intervals(s,opt);
opt.nouse_int = [];

if strcmp(opt.do,'apply')       %%%%%% apply %%%%%%%%%
    %fscore optimised on si1000p reference data
    odef={'apply' [212.5509 3967.1] 1.0681 0.0776 0.1491 0.1 0.1571 16000 0 struct struct};
    opt=fu_optstruct_init(opt,ofld,odef);
    opt.pau = fu_optstruct_init(opt.pau, {'fs' 'ret'}, {opt.fs 'smpl'});
    opt.unv = fu_optstruct_init(opt.unv, {'sts'}, {1});
    sn=fu_sylncl_sub(s,opt);
    % add syl boundaries
    if nargout>1
        sb=fu_sylbnd(s,sn,opt);
    end
else                            %%%%%% train %%%%%%%%%
    s_glob=s;
    opt_glob=opt;
    %o_opt=optimset(@fminunc);
    o_opt=optimset(@fminsearch);
    o_opt=optimset('LargeScale','on');
    % [f_lowbnd/100 f_upbndf/1000 threshold_factor ncl_length ref_length
    %  minimum_rms]
    w0=[2.3 2.9 1.06 0.08 0.14 0.16];
    
    %[w fval ef o]=fminunc(@fu_sylncl_err,w0,o_opt);
    [w fval ef o]=fminsearch(@fu_sylncl_err,w0,o_opt);
    opt=fu_optstruct_init(opt,ofld,{'apply' [w(1)*100 w(2)*1000] ...
        w(3) w(4) w(5) w(6) opt.fs 1});
    sn=fu_sylncl_sub(s,opt);
end

if opt.verbose==1
    %[sn [sb; NaN]]
    %t=[1:length(s)]./opt.fs;
    t=[1:length(s)];
    plot(t,s);
    hold on
    %if isfield(opt,'ref')
    %    for i=opt.ref; plot([i i],[-1 1],'-g'); end
    %end
    for i=sn; plot([i i],[-1 1],'-r'); end
    if nargout>1
        for i=sb; plot([i i],[-1 1],'-g'); end
    end
end
 
if strcmp(opt.do,'train')
    opt.do='apply';
    opt.error=fval;
    sn=opt;
    sn_opt=opt;
    save('sn_opt','sn_opt');
end

return
