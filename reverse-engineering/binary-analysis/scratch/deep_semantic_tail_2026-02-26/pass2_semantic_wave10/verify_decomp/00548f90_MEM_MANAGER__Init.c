/* address: 0x00548f90 */
/* name: MEM_MANAGER__Init */
/* signature: uint __thiscall MEM_MANAGER__Init(void * this, int param_1, int param_2) */


uint __thiscall MEM_MANAGER__Init(void *this,int param_1,int param_2)

{
  uint uVar1;
  int iVar2;

  DAT_009c6334 = 1;
  *(undefined4 *)((int)this + 0xc) = 0;
  uVar1 = CMemoryManager__Init(param_1,0x4b000,s_Default_heap_0065108c,1);
  DAT_009c6334 = DAT_009c6334 & uVar1;
  iVar2 = CMemoryManager__Init(0x23f000,0,s_Dump_memory_heap_00651078,1);
  if (iVar2 == 0) {
    return 0;
  }
  *(int *)((int)this + 0x1a0) = (int)this + 0xae0;
  iVar2 = CMemoryManager__Init(0x1e87800,0,s_Sound_memory_heap_00651064,0);
  if (iVar2 == 0) {
    return 0;
  }
  *(undefined **)((int)this + 0x13c) = &DAT_009c5a68;
  iVar2 = CMemoryManager__Init(0x36b000,0x32000,s_Thing_memory_heap_00651050,0);
  if (iVar2 == 0) {
    return 0;
  }
  *(undefined **)((int)this + 0x2c) = &DAT_009c519c;
  *(undefined **)((int)this + 0x28) = &DAT_009c519c;
  *(undefined **)((int)this + 0x24) = &DAT_009c519c;
  *(undefined **)((int)this + 0x44) = &DAT_009c519c;
  *(undefined **)((int)this + 0x104) = &DAT_009c519c;
  *(undefined **)((int)this + 0x100) = &DAT_009c519c;
  *(undefined **)((int)this + 0x68) = &DAT_009c519c;
  *(undefined **)((int)this + 0x174) = &DAT_009c519c;
  *(undefined **)((int)this + 0x30) = &DAT_009c519c;
  *(undefined **)((int)this + 0x4c) = &DAT_009c519c;
  *(undefined **)((int)this + 0x40) = &DAT_009c519c;
  *(undefined **)((int)this + 0x34) = &DAT_009c519c;
  *(undefined **)((int)this + 0x48) = &DAT_009c519c;
  *(undefined **)((int)this + 0xa4) = &DAT_009c519c;
  *(undefined **)((int)this + 0x10c) = &DAT_009c519c;
  *(undefined **)((int)this + 0x6c) = &DAT_009c519c;
  *(undefined **)((int)this + 0x1c0) = &DAT_009c519c;
  *(undefined **)((int)this + 0x188) = &DAT_009c519c;
  *(undefined **)((int)this + 0x180) = &DAT_009c519c;
  *(undefined **)((int)this + 0xfc) = &DAT_009c519c;
  *(undefined **)((int)this + 0x3c) = &DAT_009c519c;
  *(undefined **)((int)this + 0x7c) = &DAT_009c519c;
  *(undefined **)((int)this + 0x1fc) = &DAT_009c519c;
  *(undefined **)((int)this + 0x38) = &DAT_009c519c;
  return DAT_009c6334;
}
