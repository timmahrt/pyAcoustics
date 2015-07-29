function wi = fu_i_window(i,wl,l)

% wi = fu_i_window(i,wl,l)
% i: index in vector
% wl: window length
% l: vector length
% wi: indices in window around i
% - returns indices of window around index i in vector of length l
% - if distance from i to end or beginning of vector is less than wl/2,
%   the window is shifted accordingly

hwl=floor(wl/2);
wi=max(i-hwl,1):min(i+hwl,l);

% if window too short: trying to lengthen window to wanted size
d=wl-length(wi);
if d>0
    if wi(1)>1
        o=max(wi(1)-d,1);
        wi=o:wi(end);
        d=wl-length(wi);
    end
    if d>0
        if wi(end)<l
            o=min(wi(end)+d,l);
            wi=wi(1):o;
        end
    end
end

return
