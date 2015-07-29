function [voi zrr] = fu_voicing_sub(y,opt);

% returns binary vector (1=voiced frame) for signal vector Y
% and specs given in OPT
% called by fu_voicing

zr = fu_zero_crossing_rate(y,opt.sr,opt);
voi=zeros(length(zr),1);
voi(find(zr<opt.zr_th & zr>0))=1;

if opt.min_nf>1
    voi=fu_smooth_binvec(voi,opt.min_nf);
end


if nargout==2; zrr=zr; end

return
