/* address: 0x0044a930 */
/* name: OID__GetAttachmentOrBaseOrientationMatrix */
/* signature: void __thiscall OID__GetAttachmentOrBaseOrientationMatrix(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall OID__GetAttachmentOrBaseOrientationMatrix(void *this,int param_1,void *param_2)

{
  int iVar1;
  undefined4 *puVar2;
  float local_40;
  float fStack_3c;
  float fStack_38;
  undefined4 local_30 [12];

  if (*(int *)((int)this + 0xc) != -1) {
    (**(code **)(**(int **)((int)this + 8) + 0x160))
              (*(undefined4 *)((int)this + 0x10),*(int *)((int)this + 0xc),&local_40,local_30);
    if (((local_40 != _DAT_005d856c) || (fStack_3c != _DAT_005d856c)) ||
       (fStack_38 != _DAT_005d856c)) {
      puVar2 = local_30;
      for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
        *(undefined4 *)param_1 = *puVar2;
        puVar2 = puVar2 + 1;
        param_1 = (int)(param_1 + 4);
      }
      return;
    }
  }
  puVar2 = (undefined4 *)(*(int *)((int)this + 8) + 0x3c);
  for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
    *(undefined4 *)param_1 = *puVar2;
    puVar2 = puVar2 + 1;
    param_1 = (int)(param_1 + 4);
  }
  return;
}
