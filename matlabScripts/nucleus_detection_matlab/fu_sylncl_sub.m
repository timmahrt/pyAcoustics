function t=fu_sylncl_sub(s,opt);

% returns samples of syllable nuclei given signal S and processing
% options OPT (see fu_sylncl for details)
% called by fu_sylncl

% recall higher before 2. nucl splitting. why???

%% settings %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% reference window span
rws = floor(opt.rlength*opt.fs);
% signal length
ls=length(s);
% window length for energy calculation in samples
ml=floor(opt.length*opt.fs);
% minimum distance between subsequent nuclei in samples
md=floor(opt.md*opt.fs);
% stepsize
sts=max(1,floor(0.03*opt.fs));
stsh=floor(sts/2); % for centering of reference window

%% no use intervals (pause, voiceless) %%%%%%%%%%%%%%%%%%%%
% -> vector of all samples not to be used
t_nou_init = [];
t_nou_pau=[];
voi=[];
t_nou=[];
if isfield(opt,'nouse_int')
    t_nou_init = opt.nouse_int;
end
if opt.do_nouse>0
   if opt.do_nouse < 3
       t_nou_pau = fu_pause_detector(s,opt.pau);
   end
   if (opt.do_nouse==1 | opt.do_nouse==3)
       [voi zrr] = fu_voicing(s,opt.fs,opt.unv);
   end 
end
for i=1:size(t_nou_init,1)
    t_nou=[t_nou t_nou_init(i,1):t_nou_init(i,2)];
end
for i=1:size(t_nou_pau,1)
    t_nou=[t_nou t_nou_pau(i,1):t_nou_pau(i,2)];
end
t_nou=unique([t_nou find(voi==0)']);


%%%% filtering %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if length(opt.bf)==1; ft='low';
else; ft='band'; end

ord=5; % filter order, the higher the steeper, but incapable to filter
       % narrow bands
s=fu_filter(s,ft,opt.bf,opt.fs,ord);

%%%% settings 2 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% minimum energy as portion of maximum energy found
e_y=[];
for i=1:sts:ls
    %%%% window %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    yi=i:min(ls,i+ml-1);
    y=s(yi);
    e_y = [e_y fu_rmse(y)];
end

e_min=opt.e_min*max(e_y);
mey=max(e_y);
                                                                                

% output vector collecting nucleus sample indices
t=[];

all_i=[];
all_e=[];
all_r=[];


for i=1:sts:ls
    yi=fu_i_window(i,ml,ls);
    y=s(yi);
    e_y = fu_rmse(y);
    rwi = fu_i_window(i,rws,ls);
    rw = s(rwi);
    e_rw=fu_rmse(rw);
    all_i=[all_i i];
    all_e=[all_e e_y];
    all_r=[all_r e_rw];
end

lmopt=struct;

lmopt.peak.mpd = floor(opt.fs*opt.md/sts);
[pks idx] = fu_locmax(all_e,lmopt);
t=[];
for i=idx
   if (all_e(i) >= all_r(i)*opt.f_thresh & all_e(i) > e_min)
       if length(find(t_nou==all_i(i)))==0
           t=[t; all_i(i)];
       end
   end
end



return


