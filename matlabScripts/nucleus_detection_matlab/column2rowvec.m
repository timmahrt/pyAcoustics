function v=column2rowvec(v)

% transposition in case input is column vector

if length(v(1,:))==1
    v=v';
end

return
