%   Bootstrap script for Uwe Reichels nucleus detection.  Written by Tim Mahrt
function[] = detect_syllable_nuclei(path_to_files, output_path)

files = dir(fullfile(path_to_files,'*.wav'));
for file = files'
    [tossPath, name, tossExt] = fileparts(file.name);
    
    [y fs] = audioread(fullfile(path_to_files, file.name));
    opt.fs = fs;
    opt.verbose = 0;
    sn = fu_sylncl(y,opt);
    
    sn = sn ./ fs; % Get the timestamps in seconds
    
    output_fn = fullfile(output_path,strcat(name,'.txt'));
    fd = fopen(output_fn,'w');
    fprintf(fd,'%f\n',sn);
    fclose(fd);
end

end
