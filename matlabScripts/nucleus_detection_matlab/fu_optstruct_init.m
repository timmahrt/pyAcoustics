function opt = fu_optstruct_init(opt,optfields,optdefaults)

%opt = fu_optstruct_init(opt,optfields,optdefaults)
%initialisation of option structure OPT
%assigns each field given in cell array OPTFIELDS with corresponding
%default value given in cell array OPTDEFAULTS, whenever field is not
%yet specified
%if OPTDEFAULTS{i} is 'oblig' then optfields{i} had already to be set
%by the user. If not, an error is given.

for n=1:length(optfields)
    if ~isfield(opt,optfields{n})
        if (~isnumeric(optdefaults{n}) & strcmp(optdefaults{n},'oblig'))
            error(sprintf('opt field "%s" has to be defined by the user!',optfields{n}));
        end
        opt=setfield(opt,optfields{n},optdefaults{n});
    end
end

return
