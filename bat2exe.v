import os
import encoding.base64

fn main() {
	args := os.args
	if args.len < 2 {
		println('Usage: v_bat_to_exe <path_to_batch_file>')
		return
	}

	bat_path := os.real_path(args[1])
	if !os.exists(bat_path) {
		println('Error: File not found at ${bat_path}')
		return
	}

	target_dir := os.dir(bat_path)
	bat_bytes := os.read_bytes(bat_path) or {
		println('Error: Cannot read file')
		return
	}

	b64_content := base64.encode(bat_bytes)

	v_code := 'import os
import encoding.base64

fn main() {
	b64_data := "${b64_content}"
	decoded_bytes := base64.decode(b64_data)
	os.write_file_array(\'temp_run.bat\', decoded_bytes) or { return }
	os.system(\'temp_run.bat\')
	os.rm(\'temp_run.bat\') or {}
}
'

	temp_v_path := os.join_path(target_dir, 'temp_build.v')
	os.write_file(temp_v_path, v_code) or {
		println('Error: Cannot write temporary V file')
		return
	}

	output_exe_path := os.join_path(target_dir, 'output.exe')

	comp_res := os.execute('v -o "${output_exe_path}" "${temp_v_path}"')
	
	if comp_res.exit_code != 0 {
		println('Error: Compilation failed')
		println(comp_res.output)
		os.rm(temp_v_path) or {}
		return
	}

	os.rm(temp_v_path) or {}
	println('Success: Executable created at ${output_exe_path}')
}