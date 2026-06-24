/* address: 0x0044a850 */
/* name: OID__GetAttachmentOrOriginTransform */
/* signature: void __thiscall OID__GetAttachmentOrOriginTransform(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall OID__GetAttachmentOrOriginTransform(void *this,int param_1,void *param_2)

{
  int iVar1;
  float unaff_ESI;
  float unaff_EDI;
  undefined1 local_40 [16];
  undefined1 local_30 [36];
  float *pfStack_c;

  if (*(int *)((int)this + 0xc) == -1) {
    iVar1 = *(int *)((int)this + 8);
    *(undefined4 *)param_1 = *(undefined4 *)(iVar1 + 0x1c);
    *(undefined4 *)(param_1 + 4) = *(undefined4 *)(iVar1 + 0x20);
    *(undefined4 *)(param_1 + 8) = *(undefined4 *)(iVar1 + 0x24);
    *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(iVar1 + 0x28);
    return;
  }
  (**(code **)(**(int **)((int)this + 8) + 0x160))
            (*(undefined4 *)((int)this + 0x10),*(int *)((int)this + 0xc));
  if ((((float)local_40 == _DAT_005d856c) && ((float)local_30 == _DAT_005d856c)) &&
     (unaff_EDI == _DAT_005d856c)) {
    iVar1 = *(int *)((int)this + 8);
    *pfStack_c = *(float *)(iVar1 + 0x1c);
    pfStack_c[1] = *(float *)(iVar1 + 0x20);
    pfStack_c[2] = *(float *)(iVar1 + 0x24);
    pfStack_c[3] = *(float *)(iVar1 + 0x28);
    return;
  }
  *pfStack_c = (float)local_40;
  pfStack_c[1] = (float)local_30;
  pfStack_c[2] = unaff_EDI;
  pfStack_c[3] = unaff_ESI;
  return;
}
