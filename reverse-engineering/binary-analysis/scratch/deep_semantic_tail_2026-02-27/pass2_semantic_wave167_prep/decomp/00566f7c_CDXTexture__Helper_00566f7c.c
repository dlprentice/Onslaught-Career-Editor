/* address: 0x00566f7c */
/* name: CDXTexture__Helper_00566f7c */
/* signature: void __cdecl CDXTexture__Helper_00566f7c(void * param_1) */


void __cdecl CDXTexture__Helper_00566f7c(void *param_1)

{
  VirtualFree(*(LPVOID *)((int)param_1 + 0x10),0,0x8000);
  if (PTR_LOOP_00655da0 == param_1) {
    PTR_LOOP_00655da0 = *(undefined **)((int)param_1 + 4);
  }
  if (param_1 != &PTR_LOOP_00653d80) {
    **(undefined4 **)((int)param_1 + 4) = *(undefined4 *)param_1;
    *(undefined4 *)(*(int *)param_1 + 4) = *(undefined4 *)((int)param_1 + 4);
    HeapFree(DAT_009d35e4,0,param_1);
    return;
  }
  DAT_00653d90 = 0xffffffff;
  return;
}
