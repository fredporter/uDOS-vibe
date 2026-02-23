# Sonic Stick – USB Setup

## Capacity
- 128 GB USB 3.x (UEFI boot required)

## Recommended Partition Layout (128 GB)

```
[ ESP ]        512 MB   FAT32
[ UDOS_RO ]    8  GB    squashfs
[ UDOS_RW ]    8  GB    ext4
[ SWAP ]       8  GB    swap
[ WIZARD ]     20 GB    ext4
[ WIN10 ]      48 GB    NTFS
[ MEDIA ]      28 GB    exFAT
[ CACHE ]      ~7.5 GB  ext4
```

## Boot Behaviour
- Boots via UEFI only
- Secure Boot disabled (v0)
- Always boots into uDOS Core (Alpine)
