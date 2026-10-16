-- Optional user-run provisioning. No start, deletion or modification of an existing VM.
-- Usage: osascript infra/utm/create.applescript ABS_IMAGE ABS_SEED UNIQUE_NAME
on run argv
    if (count of argv) is not 3 then error "Pass absolute image path, seed ISO path and unique VM name"
    set diskImage to POSIX file (item 1 of argv)
    set seedImage to POSIX file (item 2 of argv)
    set vmName to item 3 of argv
    tell application "UTM"
        if exists (virtual machine named vmName) then error "VM name already exists; refusing modification"
        set vm to make new virtual machine with properties {backend:qemu, configuration:{name:vmName, architecture:"aarch64", memory:8192, cpu cores:4, hypervisor:true, uefi:true, drives:{{source:diskImage, guest size:19456}, {source:seedImage, removable:true}}}}
        update configuration of vm with {directory share mode:none, network interfaces:{{index:0, mode:emulated, port forwards:{{protocol:«constant NtPrTcPp», host address:"127.0.0.1", host port:22227, guest port:22}}}}}
        return id of vm
    end tell
end run
