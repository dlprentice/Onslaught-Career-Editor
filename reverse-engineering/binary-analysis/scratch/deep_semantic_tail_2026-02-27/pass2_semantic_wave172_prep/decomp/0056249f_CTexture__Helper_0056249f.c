/* address: 0x0056249f */
/* name: CTexture__Helper_0056249f */
/* signature: int CTexture__Helper_0056249f(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_0056249f(void)

{
  bool bVar1;
  undefined3 extraout_var;
  void *pvVar2;
  int iVar3;
  uint in_stack_00000004;
  void *in_stack_00000008;
  uint in_stack_0000001c;

  bVar1 = CRT__AdjustFloatingPointForFormatFlags
                    (in_stack_00000004,&stack0x00000014,in_stack_0000001c);
  if (CONCAT31(extraout_var,bVar1) == 0) {
    CRT__RaiseFloatingPointException();
  }
  pvVar2 = (void *)CTexture__Helper_00562ad6(in_stack_00000004);
  if ((DAT_006561f0 == 0) && (pvVar2 != (void *)0x0)) {
    iVar3 = CDXTexture__ValidateSourceAndSetLoadErrorClass(pvVar2,in_stack_00000008);
    return iVar3;
  }
  CDXTexture__SetLoadErrorClassBySourceKind((int)pvVar2);
  iVar3 = CTexture__Helper_00562c76();
  return iVar3;
}
