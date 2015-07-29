function sflt=fu_filter(s,t,gf,fs,o);

%sflt=fu_filter(s,t,gf,fs);
%s: signal vector
%t: type 'high'|'low'|'stop'|'band'
%gf: grenzfrequenzen (1 Wert --> Hoch-, Tiefpass, 2 Werte --> Bandpass)
%fs: sample frequency
%o: order, default 10
%applies butter filter
%operates only if gf < fs/2

fn=gf/(fs/2);

if fn>=1
    sflt=s;
    return
end

if nargin < 5; o=5; end

if strcmp(t,'band')
  [b a]=butter(o,fn);
else
  [b a]=butter(o, fn, t);
end

sflt=filtfilt(b,a,s);

if length(find(isnan(sflt)))>0
    disp('filtering not possible, returning original signal');
    sflt=s;
end

%freqz(b,a,128,fs);
%subplot(2,1,1)
%x=32000:32000+fs;
%plot(x,s(x),'-b')
%subplot(2,1,2)
%plot(x,sflt(x),'-b')
%a=300000;
%fhpt_play(sflt*a);

return
