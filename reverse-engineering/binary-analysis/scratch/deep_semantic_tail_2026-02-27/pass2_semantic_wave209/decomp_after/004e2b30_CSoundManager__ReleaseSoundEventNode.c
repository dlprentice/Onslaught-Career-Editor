/* address: 0x004e2b30 */
/* name: CSoundManager__ReleaseSoundEventNode */
/* signature: void __fastcall CSoundManager__ReleaseSoundEventNode(void * param_1) */


void __fastcall CSoundManager__ReleaseSoundEventNode(void *param_1)

{
  void *pvVar1;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d4c58;
  local_c = ExceptionList;
  pvVar1 = *(void **)((int)param_1 + 0x70);
  local_4 = 0;
  ExceptionList = &local_c;
  if (pvVar1 != (void *)0x0) {
    ExceptionList = &local_c;
    CSoundManager__SoundEventNode__UnlinkFromGlobalList(pvVar1);
    OID__FreeObject(pvVar1);
    *(undefined4 *)((int)param_1 + 0x70) = 0;
  }
  local_4 = 0xffffffff;
  if ((*(int *)param_1 != 0) && (pvVar1 = *(void **)(*(int *)param_1 + 4), pvVar1 != (void *)0x0)) {
    CSPtrSet__Remove(pvVar1,param_1);
  }
  ExceptionList = local_c;
  return;
}
